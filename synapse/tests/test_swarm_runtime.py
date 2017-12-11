
import time

import synapse.cortex as s_cortex
import synapse.daemon as s_daemon
import synapse.telepath as s_telepath
import synapse.lib.service as s_service
import synapse.swarm.runtime as s_runtime

from synapse.tests.common import *

class SwarmRunBase(SynTest):

    def getSwarmEnv(self):
        tenv = TstEnv()

        core0 = s_cortex.openurl('ram://')
        core1 = s_cortex.openurl('ram://')

        self.addTstForms(core0)
        self.addTstForms(core1)

        tenv.add('core0', core0, fini=True)
        tenv.add('core1', core1, fini=True)

        tufo0 = core0.formTufoByProp('strform', 'baz', foo='visi')
        tufo1 = core0.formTufoByProp('strform', 'faz', foo='visi')
        tufo2 = core1.formTufoByProp('strform', 'lol', foo='visi')
        tufo3 = core1.formTufoByProp('strform', 'hai', foo='visi')

        tufo4 = core0.formTufoByProp('intform', 10, foo='visi')
        tufo5 = core1.formTufoByProp('intform', 12, foo='romp')

        tenv.add('tufo0', tufo0)
        tenv.add('tufo1', tufo1)
        tenv.add('tufo2', tufo2)
        tenv.add('tufo3', tufo3)

        dmon = s_daemon.Daemon()
        link = dmon.listen('tcp://127.0.0.1:0')

        tenv.add('link', link)
        tenv.add('dmon', dmon, fini=True)

        port = link[1].get('port')

        svcbus = s_service.SvcBus()
        tenv.add('svcbus', svcbus, fini=True)

        dmon.share('syn.svcbus', svcbus)

        svcrmi = s_telepath.openurl('tcp://127.0.0.1/syn.svcbus', port=port)
        tenv.add('svcrmi', svcrmi, fini=True)

        s_service.runSynSvc('cortex', core0, svcrmi, tags=('hehe.haha',))
        s_service.runSynSvc('cortex', core1, svcrmi, tags=('hehe.hoho',))

        runt = s_runtime.Runtime(svcrmi)

        tenv.add('runt', runt, fini=True)

        return tenv

class SwarmRunTest(SwarmRunBase):

    def test_swarm_runtime_eq(self):
        tenv = self.getSwarmEnv()

        answ = tenv.runt.ask('strform="baz"')
        data = answ.get('data')

        self.eq(data[0][0], tenv.tufo0[0])

        # FIXME check for other expected results info!

        answ = tenv.runt.ask('strform:foo')
        data = answ.get('data')

        self.eq(len(data), 4)

        answ = tenv.runt.ask('hehe.haha/strform:foo')
        data = answ.get('data')

        self.eq(len(data), 2)

        answ = tenv.runt.ask('hehe.haha/strform:foo="visi"')
        data = answ.get('data')

        self.eq(len(data), 2)

        tenv.fini()

    def test_swarm_runtime_pivot(self):
        tenv = self.getSwarmEnv()

        data = tenv.runt.eval('strform="baz" strform:foo->strform:foo')

        self.eq(len(data), 4)

        tenv.fini()

    def test_swarm_runtime_opts(self):
        tenv = self.getSwarmEnv()

        answ = tenv.runt.ask('%foo')
        self.eq(answ['options'].get('foo'), 1)

        answ = tenv.runt.ask('opts(foo=10)')
        self.eq(answ['options'].get('foo'), 10)

        answ = tenv.runt.ask('%foo=10')
        self.eq(answ['options'].get('foo'), 10)

        answ = tenv.runt.ask('opts(foo="bar")')
        self.eq(answ['options'].get('foo'), 'bar')

        answ = tenv.runt.ask('%foo="bar"')
        self.eq(answ['options'].get('foo'), 'bar')

        tenv.fini()

    def test_swarm_runtime_opts_uniq(self):
        tenv = self.getSwarmEnv()

        answ = tenv.runt.ask('%uniq strform="baz" strform="baz"')
        self.eq(len(answ['data']), 1)

        answ = tenv.runt.ask('%uniq=0 strform="baz" strform="baz"')
        self.eq(len(answ['data']), 2)

        tenv.fini()

    def test_swarm_runtime_join(self):
        tenv = self.getSwarmEnv()

        answ = tenv.runt.ask('strform="baz" join("strform:foo")')
        data = answ.get('data')

        self.eq(len(data), 4)

        answ = tenv.runt.ask('strform="baz" join("intform:foo","strform:foo")')
        data = answ.get('data')

        self.eq(len(data), 2)

        tenv.fini()

    def test_swarm_runtime_gele(self):
        env = self.getSwarmEnv()

        answ = env.runt.ask('intform>=11')

        data = answ.get('data')
        self.eq(len(data), 1)
        self.eq(data[0][1].get('intform'), 12)

        answ = env.runt.ask('intform>10')

        data = answ.get('data')
        self.eq(len(data), 1)
        self.eq(data[0][1].get('intform'), 12)

        answ = env.runt.ask('intform>=10')

        data = answ.get('data')
        self.eq(len(data), 2)

        answ = env.runt.ask('intform<=11')

        data = answ.get('data')
        self.eq(len(data), 1)
        self.eq(data[0][1].get('intform'), 10)

        answ = env.runt.ask('intform<12')

        data = answ.get('data')
        self.eq(len(data), 1)
        self.eq(data[0][1].get('intform'), 10)

        answ = env.runt.ask('intform<=13')

        data = answ.get('data')
        self.eq(len(data), 2)

        answ = env.runt.ask('intform -intform<=11')

        data = answ.get('data')
        self.eq(len(data), 1)

        env.fini()

    def test_swarm_runtime_regex(self):
        env = self.getSwarmEnv()
        answ = env.runt.ask('strform +strform~="^l"')

        data = answ.get('data')
        self.eq(data[0][1].get('strform'), 'lol')

        answ = env.runt.ask('strform +strform~="^Q"')
        self.eq(len(answ.get('data')), 0)

        answ = env.runt.ask('strform +strform~="^Q"')
        self.eq(len(answ.get('data')), 0)

        answ = env.runt.ask('strform -strform~="^[a-z]{3}$"')
        self.eq(len(answ.get('data')), 0)

        env.fini()

    def test_swarm_runtime_or(self):

        env = self.getSwarmEnv()
        answ = env.runt.ask('strform +strform="baz"|strform="faz"')

        tufos = answ.get('data')

        foobars = sorted([t[1].get('strform') for t in tufos])

        self.eq(foobars, ['baz', 'faz'])

        env.fini()

    def test_swarm_runtime_and(self):

        with self.getSwarmEnv() as env:

            answ = env.runt.ask('strform -strform="baz" & strform:foo="newp" ')

            tufos = answ.get('data')

            foobars = sorted([t[1].get('strform') for t in tufos])

            self.eq(foobars, ['baz', 'faz', 'hai', 'lol'])

    def test_swarm_runtime_clear(self):

        env = self.getSwarmEnv()
        answ = env.runt.ask('strform clear()')

        tufos = answ.get('data')
        self.eq(len(tufos), 0)

        env.fini()

    def test_swarm_runtime_saveload(self):

        env = self.getSwarmEnv()
        answ = env.runt.ask('strform="baz" save("woot") clear() load("woot")')

        tufos = answ.get('data')

        self.eq(len(tufos), 1)
        self.eq(tufos[0][1].get('strform'), 'baz')

        env.fini()

    def test_swarm_runtime_has(self):

        env = self.getSwarmEnv()

        # use the lift code for has()
        answ = env.runt.ask('strform')

        tufos = answ.get('data')

        self.eq(len(tufos), 4)
        self.eq(tufos[0][1].get('node:form'), 'strform')

        # use the filter code for has()
        answ = env.runt.ask('node:form +strform')

        tufos = answ.get('data')

        self.eq(len(tufos), 4)
        self.eq(tufos[0][1].get('node:form'), 'strform')

        env.fini()

    def test_swarm_runtime_maxtime(self):

        env = self.getSwarmEnv()
        self.raises(HitStormLimit, env.runt.eval, 'strform', timeout=0)
        env.fini()

    def test_swarm_runtime_by(self):

        env = self.getSwarmEnv()

        answ = env.runt.ask('intform*range=(10,13)')
        tufos = answ.get('data')

        self.eq(len(tufos), 2)

        answ = env.runt.ask('intform*range=(10,12)')
        tufos = answ.get('data')

        self.eq(len(tufos), 1)

        answ = env.runt.ask('intform^1*range=(10,13)')
        tufos = answ.get('data')

        self.eq(len(tufos), 2)

        env.fini()

    def test_swarm_runtime_frob(self):

        env = self.getSwarmEnv()

        env.core0.formTufoByProp('inet:ipv4', 0x01020304)

        answ = env.runt.ask('inet:ipv4="1.2.3.4"')

        tufos = answ.get('data')
        self.eq(len(tufos), 1)
        self.eq(tufos[0][1].get('inet:ipv4'), 0x01020304)

        answ = env.runt.ask('inet:ipv4=0x01020304')

        tufos = answ.get('data')
        self.eq(len(tufos), 1)
        self.eq(tufos[0][1].get('inet:ipv4'), 0x01020304)

        env.fini()
