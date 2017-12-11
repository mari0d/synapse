import unittest

import synapse.cortex as s_cortex
import synapse.lib.tags as s_tags

from synapse.tests.common import *

class TagTest(SynTest):

    def test_aspect_iter_up(self):
        tags = tuple(s_tags.iterTagUp('foo.bar.baz'))
        self.eq(tags, ('foo.bar.baz', 'foo.bar', 'foo'))

    def test_aspect_iter_down(self):
        tags = tuple(s_tags.iterTagDown('foo.bar.baz'))
        self.eq(tags, ('foo', 'foo.bar', 'foo.bar.baz'))

    def test_aspect_adddel(self):

        with self.getRamCore() as core:
            tufo = core.formTufoByProp('strform', 'bar')
            tufo = core.addTufoTag(tufo, 'baz.faz.gaz')

            self.nn(tufo[1].get('#baz'))
            self.nn(tufo[1].get('#baz.faz'))
            self.nn(tufo[1].get('#baz.faz.gaz'))

            tufos = core.getTufosByTag('baz.faz', form='strform')

            self.eq(len(tufos), 1)

            tufo = core.delTufoTag(tufo, 'baz.faz')

            tufos = core.getTufosByTag('baz.faz', form='strform')
            self.eq(len(tufos), 0)

            tufos = core.getTufosByTag('baz.faz.gaz', form='strform')
            self.eq(len(tufos), 0)

    def test_aspect_bytag(self):
        bytag = s_tags.ByTag()

        bytag.put('foo0', ('foos.foo0', 'bar.baz'))
        bytag.put('foo1', ('foos.foo1', 'bar.faz'))

        vals = tuple(sorted(bytag.get('bar')))
        self.eq(vals, ('foo0', 'foo1'))

        vals = tuple(sorted(bytag.get('foos')))
        self.eq(vals, ('foo0', 'foo1'))

        vals = tuple(sorted(bytag.get('foos.foo0')))
        self.eq(vals, ('foo0',))

        vals = tuple(sorted(bytag.get('newp.foo0')))
        self.eq(vals, ())

        bytag.pop('foo0')

        vals = tuple(sorted(bytag.get('foos')))
        self.eq(vals, ('foo1',))

    def test_tags_subs(self):
        tufo = ('lolz', {'node:form': 'woot'})
        self.false(s_tags.getTufoSubs(tufo, 'mytag'))

        tufo = ('lolz', {'node:form': 'woot', '#mytag': 1})
        self.true(s_tags.getTufoSubs(tufo, 'mytag'))
