import regex

import synapse.lib.cmdr as s_cmdr
import synapse.cmds.cortex as s_cmds_cortex

from synapse.tests.common import *

class SynCmdCoreTest(SynTest):

    def getCoreCmdr(self, core):
        outp = s_output.OutPutStr()
        return s_cmdr.getItemCmdr(core, outp=outp)

    def test_cmds_help(self):
        with self.getDmonCore() as core:
            outp = s_output.OutPutStr()
            cmdr = s_cmdr.getItemCmdr(core, outp=outp)
            cmdr.runCmdLine('help')
            self.true(str(outp).find('List commands and display help output.') != -1)

    def test_cmds_quit(self):
        with self.getDmonCore() as core:
            outp = s_output.OutPutStr()
            cmdr = s_cmdr.getItemCmdr(core, outp=outp)
            cmdr.runCmdLine('quit')
            self.true(str(outp).find('o/') != -1)

    def test_cmds_ask(self):
        with self.getDmonCore() as core:
            outp = s_output.OutPutStr()
            cmdr = s_cmdr.getItemCmdr(core, outp=outp)
            core.formTufoByProp('inet:email', 'visi@vertex.link')
            resp = cmdr.runCmdLine('ask inet:email="visi@vertex.link"')
            self.len(1, resp['data'])
            self.ne(str(outp).strip().find('visi@vertex.link'), -1)

    def test_cmds_ask_debug(self):
        with self.getDmonCore() as core:
            outp = s_output.OutPutStr()
            cmdr = s_cmdr.getItemCmdr(core, outp=outp)
            core.formTufoByProp('inet:email', 'visi@vertex.link')
            resp = cmdr.runCmdLine('ask --debug inet:email="visi@vertex.link"')
            self.len(1, resp['data'])

            outp = str(outp)
            terms = ('oplog', 'took', 'options', 'limits')

            for term in terms:
                self.nn(regex.search(term, outp))

    def test_cmds_ask_props(self):
        with self.getDmonCore() as core:
            outp = s_output.OutPutStr()
            cmdr = s_cmdr.getItemCmdr(core, outp=outp)
            core.formTufoByProp('inet:email', 'visi@vertex.link')
            resp = cmdr.runCmdLine('ask --props inet:email="visi@vertex.link"')
            self.len(1, resp['data'])

            outp = str(outp)
            terms = ('fqdn = vertex.link', 'user = visi')

            for term in terms:
                self.nn(regex.search(term, outp))

    def test_cmds_ask_tagtime(self):

        with self.getDmonCore() as core:

            outp = s_output.OutPutStr()
            cmdr = s_cmdr.getItemCmdr(core, outp=outp)

            resp = cmdr.runCmdLine('ask [ inet:ipv4=1.2.3.4 #foo.bar@2011-2016 #baz.faz ]')
            self.len(1, resp['data'])

            lines = [s.strip() for s in str(outp).split('\n')]

            self.true(any([regex.search('^#baz.faz \(added [0-9/: \.]+\)$', l) for l in lines]))
            self.true(any([regex.search('^#foo.bar \(added [0-9/: \.]+\) 2011/01/01 00:00:00.000  -  2016/01/01 00:00:00.000$', l) for l in lines]))

    def test_cmds_ask_mutual_exclusive(self):
        with self.getDmonCore() as core:
            outp = s_output.OutPutStr()
            cmdr = s_cmdr.getItemCmdr(core, outp=outp)
            core.formTufoByProp('inet:email', 'visi@vertex.link')
            resp = cmdr.runCmdLine('ask --raw --props inet:email="visi@vertex.link"')
            self.none(resp)
            outp = str(outp)
            self.true('Cannot specify --raw and --props together.' in outp)

    def test_cmds_ask_null_response(self):
        with self.getDmonCore() as core:
            outp = s_output.OutPutStr()
            cmdr = s_cmdr.getItemCmdr(core, outp=outp)
            core.formTufoByProp('inet:email', 'visi@vertex.link')
            resp = cmdr.runCmdLine('ask inet:email="pennywise@vertex.link"')
            self.none(resp)
            outp = str(outp)
            self.true('(0 results)' in outp)

    def test_cmds_ask_exc_response(self):
        with self.getDmonCore() as core:
            outp = s_output.OutPutStr()
            cmdr = s_cmdr.getItemCmdr(core, outp=outp)
            core.formTufoByProp('inet:email', 'visi@vertex.link')
            resp = cmdr.runCmdLine('ask inet:dns:a:ipv4*inet:cidr=192.168.0.0/100')
            self.none(resp)

            outp = str(outp)
            terms = ('\(0 results\)',
                     'oplog:',
                     'options:',
                     'limits:')
            for term in terms:
                self.nn(regex.search(term, outp))

    def test_cmds_ask_raw(self):
        with self.getDmonCore() as core:
            outp = s_output.OutPutStr()
            cmdr = s_cmdr.getItemCmdr(core, outp=outp)
            core.formTufoByProp('inet:email', 'visi@vertex.link')
            resp = cmdr.runCmdLine('ask --raw inet:email="visi@vertex.link"')
            self.len(1, resp['data'])

            outp = str(outp)
            terms = ('"node:form": "inet:email"', '"inet:email:user": "visi"')
            for term in terms:
                self.nn(regex.search(term, outp))

    def test_cmds_ask_multilift(self):
        with self.getDmonCore() as core:
            outp = s_output.OutPutStr()
            cmdr = s_cmdr.getItemCmdr(core, outp=outp)
            core.formTufoByProp('strform', 'hehe')
            core.formTufoByProp('inet:ipv4', 0)
            resp = cmdr.runCmdLine('ask strform inet:ipv4')
            self.len(2, resp['data'])

            outp = str(outp)
            terms = ('0.0.0.0', 'hehe')

            for term in terms:
                self.nn(regex.search(term, outp))

    def test_cmds_ask_noopts(self):
        with self.getDmonCore() as core:
            outp = s_output.OutPutStr()
            cmdr = s_cmdr.getItemCmdr(core, outp=outp)
            cmdr.runCmdLine('ask')
            self.nn(regex.search('Examples:', str(outp)))

    def test_cmds_guid(self):
        with self.getDmonCore() as core:
            outp = s_output.OutPutStr()
            cmdr = s_cmdr.getItemCmdr(core, outp=outp)
            cmdr.runCmdLine('guid')
            self.ne(str(outp).find('new guid:'), -1)

    def test_cmds_py(self):
        with self.getDmonCore() as core:
            outp = s_output.OutPutStr()
            cmdr = s_cmdr.getItemCmdr(core, outp=outp)
            cmdr.runCmdLine('py 20 + 20')
            self.ne(str(outp).find('40'), -1)
