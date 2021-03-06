from synapse.tests.common import *

import synapse.lookup.phonenum as s_l_phone

class PhLookTest(SynTest):

    def test_lookup_phonenum(self):
        self.eq(s_l_phone.getPhoneInfo(18075551212)['cc'], 'ca')
        self.eq(s_l_phone.getPhoneInfo(17035551212)['cc'], 'us')
