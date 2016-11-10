from uuid import UUID, uuid4

import pytest

from fractalis.analytics import job


class TestJob(object):

    def test_exception_when_starting_non_existing_task(self):
        with pytest.raises(AttributeError):
            job.start_job('querty.tasks.add', {})
        with pytest.raises(AttributeError):
            job.start_job('test.tasks.querty', {})

    def test_exception_when_invalid_parameters(self):
        with pytest.raises(TypeError):
            job.start_job('test.tasks.add', {'a': 1})

    def test_start_job_returns_uuid(self):
        job_id = job.start_job('test.tasks.add', {'a': 1, 'b': 2})
        UUID(job_id)

    def test_finished_job_returns_results(self):
        job_id = job.start_job('test.tasks.add', {'a': 1, 'b': 2})
        async_result = job.get_job_result('test.tasks.add', job_id)
        async_result.get(timeout=1)
        assert async_result.status == 'SUCCESS'
        assert async_result.result == 3

    def test_failing_job_return_exception_message(self):
        job_id = job.start_job('test.tasks.div', {'a': 1, 'b': 0})
        async_result = job.get_job_result('test.tasks.div', job_id)
        async_result.get(timeout=1)
        assert async_result.status == 'FAILURE'
        assert 'ZeroDivisionError' in async_result.result

    def test_job_in_progress_has_running_status(self):
        job_id = job.start_job('test.tasks.do_nothing', {'time': 2})
        async_result = job.get_job_result('test.tasks.do_nothing', job_id)
        assert async_result.status == 'PENDING'

    def test_exception_when_checking_non_existing_job(self):
        with pytest.raises(LookupError):
            job.get_job_result('test.tasks.do_nothing', str(uuid4()))

    def test_job_is_gone_after_canceling(self):
        job_id = job.start_job('test.tasks.do_nothing', {'time': 10})
        job.cancel_job('test.tasks.do_nothing', job_id)
        with pytest.raises(LookupError):
            job.get_job_result(job_id)

    def test_exception_when_canceling_non_existing_job(self):
        with pytest.raises(LookupError):
            job.cancel_job('test.tasks.do_nothing', uuid4())
