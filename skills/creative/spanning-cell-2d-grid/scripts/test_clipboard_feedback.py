import asyncio
import unittest
from clipboard_feedback import ClipboardFeedback


class ClipboardTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.timers = {}
        self.serial = 0

        def schedule(cb, delay):
            self.assertEqual(delay, 1500)
            self.serial += 1
            self.timers[self.serial] = cb
            return self.serial

        self.model = ClipboardFeedback(schedule, lambda key: self.timers.pop(key, None))

    async def pending(self):
        future = asyncio.get_running_loop().create_future()
        task = asyncio.create_task(self.model.copy('root', lambda _: future))
        await asyncio.sleep(0)  # yield task admission, never wall-clock ordering
        self.assertEqual(self.model.label, 'Menyalin…')
        return future, task

    async def test_fulfillment_and_reset(self):
        future, task = await self.pending()
        self.assertFalse(self.timers)
        future.set_result(None)
        self.assertTrue((await task)['success'])
        self.assertEqual(self.model.label, 'Tersalin!')
        self.timers.popitem()[1]()
        self.assertEqual(self.model.label, 'Salin Rute')

    async def test_rejection_and_fallback_failures(self):
        future, task = await self.pending()
        future.set_exception(RuntimeError('denied'))
        self.assertFalse((await task)['success'])
        for result in (True, False, 'truthy'):
            value = await self.model.copy('root', fallback=lambda _: result)
            self.assertEqual(value['success'], result is True)
        def fail(_):
            raise RuntimeError('fallback')
        self.assertFalse((await self.model.copy('root', fallback=fail))['success'])
        self.assertEqual(self.model.label, 'Gagal menyalin')
        self.assertFalse((await self.model.copy('root'))['success'])

    async def test_overlap_and_timer_replacement(self):
        await self.model.copy('root', fallback=lambda _: True)
        old_reset = next(iter(self.timers.values()))
        old, old_task = await self.pending()
        self.assertFalse(self.timers)
        new, new_task = await self.pending()
        new.set_result(None)
        await new_task
        old.set_exception(RuntimeError('late'))
        await old_task
        old_reset()
        self.assertEqual(self.model.label, 'Tersalin!')
        self.assertEqual(len(self.timers), 1)

    async def test_rerender_and_dispose(self):
        for operation in (self.model.rerender, self.model.dispose):
            await self.model.copy('root', fallback=lambda _: True)
            old_reset = next(iter(self.timers.values()))
            future, task = await self.pending()
            operation()
            future.set_result(None)
            await task
            old_reset()
            self.assertEqual(self.model.label, 'Salin Rute')
            self.assertFalse(self.timers)
        self.assertFalse(self.model.dispose())
        self.assertFalse((await self.model.copy('root', fallback=lambda _: self.fail('disposed write')))['success'])


if __name__ == '__main__':
    unittest.main()
