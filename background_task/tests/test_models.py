# -*- coding: utf-8 -*-
from mock import patch, Mock, create_autospec
from datetime import datetime

from django.test.testcases import TransactionTestCase
from django.utils import timezone

from background_task.models import Task


@patch('background_task.models.Task.objects')
class UnlockTaskTestCase(TransactionTestCase):
    def setUp(self):
        self.task = create_autospec(Task)
        self.task.locked_by = 'locked_by'
        self.task.locked_at = timezone.now()
        self.task.run_at = timezone.now()
        self.task.task_name = 'TaskName'


    @patch('background_task.models.timezone')
    def test_unlock_clears_locked_at_and_locked_by(self, django_timezone, Task_objects):
        Task_objects.exclude.return_value.filter.return_value.exists.return_value = False
        run_at = self.task.run_at

        Task.unlock(self.task)

        self.assertIsNone(self.task.locked_by)
        self.assertIsNone(self.task.locked_at)
        self.assertEqual(self.task.run_at, django_timezone.now())

        Task_objects.exclude.assert_called_once_with(pk=self.task.pk)
        Task_objects.exclude().filter.assert_called_once_with(
            task_name=self.task.task_name,
            run_at__gte=run_at
        )

        self.task.save.assert_called_once()


    def test_unlock_sets_run_at_to_before_next_task(self, Task_objects):
        next_task = Task_objects.exclude().filter()
        next_task.exists.return_value = True
        next_task.earliest.return_value.run_at = datetime(year=2021, month=3, day=10)

        Task.unlock(self.task)

        expected = datetime(year=2021, month=3, day=9, hour=23, minute=59, second=59, microsecond=999000)
        self.assertEqual(self.task.run_at, expected)

        next_task.earliest.assert_called_once_with('run_at')
        self.task.save.assert_called_once()


class TaskRunsAsynchronouslyTestCase(TransactionTestCase):
    def setUp(self):
        self.task = create_autospec(Task)
        self.task.force_synchronous_execution = False


    @patch('background_task.models.app_settings')
    def test_not_forcing_sync_and_global_async_is_true_returns_true(self, app_settings):
        app_settings.BACKGROUND_TASK_RUN_ASYNC = True
        self.assertTrue(Task.runs_async(self.task))


    @patch('background_task.models.app_settings')
    def test_not_forcing_sync_and_global_async_is_false_returns_false(self, app_settings):
        app_settings.BACKGROUND_TASK_RUN_ASYNC = False
        self.assertFalse(Task.runs_async(self.task))


    @patch('background_task.models.app_settings')
    def test_forcing_sync_and_global_async_is_true_returns_false(self, app_settings):
        app_settings.BACKGROUND_TASK_RUN_ASYNC = True
        self.task.force_synchronous_execution = True
        self.assertFalse(Task.runs_async(self.task))


    @patch('background_task.models.app_settings')
    def test_forcing_sync_and_global_async_is_false_returns_true(self, app_settings):
        app_settings.BACKGROUND_TASK_RUN_ASYNC = False
        self.task.force_synchronous_execution = True
        self.assertFalse(Task.runs_async(self.task))
