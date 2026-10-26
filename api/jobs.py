"""Rechenaufträge: gleiche Einstellung läuft nur einmal, höchstens ``max_jobs`` gleichzeitig, Rest wartet."""
import threading
from dataclasses import asdict

from gridsim.run import cached_seeds, feeders_fingerprint


class Job:
    def __init__(self, params, status, feeders_fp=None):
        self.params = params
        self.feeders_fp = feeders_fp   # Netzstand beim Start; anderer Stand → Auftrag nicht wiederverwenden
        self.status = status   # queued | running | done | cached | error
        self.seeds = []
        self.error = None
        self.cond = threading.Condition()

    def add(self, result):
        with self.cond:
            self.seeds.append(asdict(result))
            self.cond.notify_all()

    def finish(self, status, error=None):
        with self.cond:
            self.status, self.error = status, error
            self.cond.notify_all()

    @property
    def finished(self):
        return self.status in ('done', 'cached', 'error')

    def snapshot(self):
        with self.cond:
            return {'run_id': self.params.key(), 'status': self.status, 'params': asdict(self.params),
                    'n_seeds': self.params.n_seeds, 'seeds': list(self.seeds), 'error': self.error}


class JobManager:
    def __init__(self, prepared_root, cache_dir, runner, max_jobs=2, workers=4):
        self.root, self.cache_dir, self.runner, self.workers = prepared_root, cache_dir, runner, workers
        self.jobs = {}
        self.lock = threading.Lock()
        self.slots = threading.Semaphore(max_jobs)
        self.running = 0
        self.max_jobs = max_jobs

    def submit(self, params):
        key = params.key()
        fp = feeders_fingerprint(self.root)
        with self.lock:
            job = self.jobs.get(key)
            if job and (not job.finished or (job.status != 'error' and len(job.seeds) >= params.n_seeds
                                             and job.feeders_fp == fp)):
                return job  # läuft schon oder ist fertig (mit demselben Netzstand)
            cached = cached_seeds(self.cache_dir, params, fp)
            if len(cached) >= params.n_seeds:
                job = Job(params, 'cached', fp)
                job.seeds = [asdict(r) for r in sorted(cached, key=lambda r: r.index)]
                self.jobs[key] = job
                return job
            job = Job(params, 'running' if self.running < self.max_jobs else 'queued', fp)
            self.running += 1
            self.jobs[key] = job
        threading.Thread(target=self._run, args=(job,), daemon=True).start()
        return job

    def _run(self, job):
        with self.slots:
            if job.status == 'queued':
                job.finish('running')
            try:
                for r in self.runner(self.root, job.params, workers=self.workers, cache_dir=self.cache_dir):
                    job.add(r)
                job.finish('done')
            except Exception as exc:  # Lauf darf die API nicht mitreißen
                job.finish('error', f'{type(exc).__name__}: {exc}')
            finally:
                with self.lock:
                    self.running -= 1

    def get(self, run_id):
        return self.jobs.get(run_id)
