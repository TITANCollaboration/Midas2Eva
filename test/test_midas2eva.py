#!/usr/bin/env python

import mock
from unittest import TestCase
import midas2eva


class Tests(TestCase):
    @mock.patch('midas2eva.midas2eva.os')
    def setUp(self, m_os):
        m_os.path.isfile.return_value = True
        self.M2E = midas2eva.MidasToEva("afilename.mid")

    @mock.patch('midas2eva.midas2eva.os')
    def test_init(self, m_os):
        m_os.path.isfile.return_value = True
        mym2e = midas2eva.MidasToEva("afilename.mid")

        self.assertEqual(mym2e.status, 1)
        self.assertEqual(mym2e.filename, "afilename.mid")
        m_os.path.isfile.assert_called_once_with("afilename.mid")

        m_os.reset_mock()

        m_os.path.isfile.return_value = False
        mym2e = midas2eva.MidasToEva("afilename.mid")
        self.assertEqual(mym2e.status, 0)
        m_os.path.isfile.assert_called_once_with("afilename.mid")

    @mock.patch('midas2eva.midas2eva.os')
    def test_extractXML(self, m_os):
        simplexml = ('<odb root="/">\n' +
                     '<dir name="System">\n' +
                     '<dir name="Clients">\n' +
                     '<dir name="12665">\n' +
                     '<key name="Hardware type" type="INT">44</key>\n' +
                     '<key name="Server Port" type="INT">34539</key>\n' +
                     '</dir>\n' +
                     '</dir>\n' +
                     '</dir>\n' +
                     '</odb>\n' +
                     '<odb root="/">\n' +
                     '<dir name="System">\n' +
                     '<dir name="Clients">\n' +
                     '<dir name="12665">\n' +
                     '<key name="Hardware type" type="INT">44</key>\n' +
                     '<key name="Server Port" type="INT">34539</key>\n' +
                     '</dir>\n' +
                     '</dir>\n' +
                     '</dir>\n' +
                     '</odb>\n')

        m_os.path.isfile.return_value = True
        mym2e = midas2eva.MidasToEva("afilename.mid")
        _open = mock.mock_open()
        # Test opening a file
        with mock.patch("__builtin__.open", _open):
            _open.return_value.read.return_value = simplexml
            mym2e.extractXML()

        result = mym2e.domag.find("./dir/dir/dir/[@name='12665']")\
            .find("key/[@name='Hardware type']").text
        expected = "44"
        self.assertEqual(result, expected)

        # Test with fail on opening file
        with mock.patch("__builtin__.open", _open):
            _open.return_value.read.side_effect = IOError
            mym2e.extractXML()

        self.assertEqual(mym2e.status, 0)

        # Test with __init__ failure (status = 0)
        _open2 = mock.mock_open()
        with mock.patch("__builtin__.open", _open2):
            mym2e.extractXML()
        _open2.return_value.read.assert_not_called()

    def test_getAttribute(self):
        myxmlfind2 = mock.MagicMock()
        myxmlfind2.text = "a"
        myxmlfind1 = mock.MagicMock()
        myxmlfind1.find.return_value = myxmlfind2
        myxml = mock.MagicMock()
        myxml.find.return_value = myxmlfind1

        result = self.M2E.getAttribute(myxml, "A", "B", "C")
        expected = "a"
        self.assertEqual(result, expected)
        myxmlfind1.find.assert_called_once_with("key/[@name='C']")

        myxml.find.side_effect = Exception
        self.assertRaises(Exception, self.M2E.getAttribute,
                          myxml, "a", "b", "c")

    def test_getAmplitude(self):
        self.M2E.getAttribute = mock.MagicMock(return_value=1.0)
        self.M2E.domag = ""

        # test reading from xml in midas file
        self.M2E.getAmplitude()
        self.assertEqual(self.M2E.amplitude, 1.0)
        self.M2E.getAttribute.assert_called_once_with("", './dir/dir',
                                                      'Variables',
                                                      'MPETRFAmp',
                                                      float)

        # test one of the failure modes
        self.M2E.getAttribute = mock.MagicMock(return_value=-1)
        self.M2E.getAmplitude()
        self.assertEqual(self.M2E.amplitude, -1)

        # test passing a value to the function
        self.M2E.getAmplitude(2.0)
        self.assertEqual(self.M2E.amplitude, 2.0)

    def test_getStartFreq(self):
        self.M2E.getAttribute = mock.MagicMock(return_value=1.000000)
        self.M2E.dom2ag = ""

        # test reading from xml in midas file
        self.M2E.getStartFreq()
        self.assertEqual(self.M2E.startfreq, 1000000.0)
        self.M2E.getAttribute.assert_called_once_with("", './dir/dir',
                                                      'Variables',
                                                      'StartFreq (MHz)',
                                                      float)

        # test passing a vlue to the function
        self.M2E.getStartFreq(2000000)
        self.assertEqual(self.M2E.startfreq, 2000000.0)

    def test_getStopFreq(self):
        self.M2E.getAttribute = mock.MagicMock(return_value=1.000000)
        self.M2E.dom2ag = ""

        # test reading from xml in midas file
        self.M2E.getStopFreq()
        self.assertEqual(self.M2E.stopfreq, 1000000.0)
        self.M2E.getAttribute.assert_called_once_with("", './dir/dir',
                                                      'Variables',
                                                      'EndFreq (MHz)',
                                                      float)

        # test passing a vlue to the function
        self.M2E.getStopFreq(2000000)
        self.assertEqual(self.M2E.stopfreq, 2000000.0)

    def test_getNumFreqSteps(self):
        self.M2E.getAttribute = mock.MagicMock(return_value=41.0)
        self.M2E.dom2ag = ""

        # test reading from xml in midas file
        self.M2E.getNumFreqSteps()
        self.assertEqual(self.M2E.numfreqsteps, 41.0)
        self.M2E.getAttribute.assert_called_once_with("", './dir/dir/dir/dir',
                                                      'begin_ramp',
                                                      'loop count',
                                                      float)

        # test one of the failure modes
        self.M2E.getAttribute = mock.MagicMock(return_value=-1)
        self.M2E.getNumFreqSteps()
        self.assertEqual(self.M2E.numfreqsteps, -1)

        # test passing a value to the function
        self.M2E.getNumFreqSteps(21)
        self.assertEqual(self.M2E.numfreqsteps, 21.0)

    def test_getNumCycles(self):
        self.M2E.getAttribute = mock.MagicMock(return_value=25.0)
        self.M2E.domag = ""

        # test reading from xml in midas file
        self.M2E.getNumCycles()
        self.assertEqual(self.M2E.numcycles, 25.0)
        self.M2E.getAttribute.assert_called_once_with("", './dir/dir/dir/dir',
                                                      'begin_scan',
                                                      'loop count',
                                                      float)

        # test one of the failure modes
        self.M2E.getAttribute = mock.MagicMock(return_value=-1)
        self.M2E.getNumCycles()
        self.assertEqual(self.M2E.numcycles, -1)

    def test_getStartTime(self):
        self.M2E.getAttribute = mock.MagicMock(return_value=25.0)
        self.M2E.domag = ""

        # test reading from xml in midas file
        self.M2E.getStartTime()
        self.assertEqual(self.M2E.starttime, 25.0)
        self.M2E.getAttribute.assert_called_once_with("", './dir',
                                                      'Runinfo',
                                                      'Start time binary',
                                                      float)

        # test one of the failure modes
        self.M2E.getAttribute = mock.MagicMock(return_value=-1)
        self.M2E.getStartTime()
        self.assertEqual(self.M2E.starttime, -1)

    def test_getEndTime(self):
        self.M2E.getAttribute = mock.MagicMock(return_value=25.0)
        self.M2E.dom2ag = ""

        # test reading from xml in midas file
        self.M2E.getEndTime()
        self.assertEqual(self.M2E.endtime, 25.0)
        self.M2E.getAttribute.assert_called_once_with("", './dir',
                                                      'Runinfo',
                                                      'Stop time binary',
                                                      float)

        # test one of the failure modes
        self.M2E.getAttribute = mock.MagicMock(return_value=-1)
        self.M2E.getEndTime()
        self.assertEqual(self.M2E.endtime, -1)

    def test_getElem(self):
        self.M2E.getAttribute = mock.MagicMock(return_value="1K39")
        self.M2E.domag = ""

        self.M2E.getElem()
        self.assertEqual(self.M2E.mass, "1K39")
        self.M2E.getAttribute.assert_called_once_with("", './dir/dir',
                                                      'Variables',
                                                      'Species',
                                                      str)

        self.M2E.getAttribute = mock.MagicMock(return_value=-1)
        self.M2E.getElem()
        self.assertEqual(self.M2E.mass, -1)

        self.M2E.getElem("1K41")
        self.assertEqual(self.M2E.mass, "1K41")

    def test_getZ(self):
        self.M2E.getAttribute = mock.MagicMock(return_value="1; 2; 3")
        self.M2E.domag = ""

        self.M2E.getZ()
        self.assertEqual(self.M2E.charge, 1)
        self.M2E.getAttribute.assert_called_once_with("", './dir/dir',
                                                      'Variables',
                                                      'Charge')

        self.M2E.getAttribute = mock.MagicMock(return_value="-1")
        self.M2E.getZ()
        self.assertEqual(self.M2E.charge, -1)

        self.M2E.getZ("10")
        self.assertEqual(self.M2E.charge, 10)

    def test_getRFTime(self):
        self.M2E.getAttribute = mock.MagicMock(side_effect=[100.0, 100.0])
        self.M2E.domag = ""

        self.M2E.getRFTime()
        self.assertEqual(self.M2E.trf, 0.2)
        self.assertEqual(self.M2E.getAttribute.call_count, 3)

        self.M2E.getRFTime(0.1)
        self.assertEqual(self.M2E.trf, 0.1)

    def test_setTdcGateWidth(self):
        self.M2E.getAttribute = mock.MagicMock(return_value=0.1)  # in ms
        self.M2E.domag = ""

        self.M2E.setTdcGateWidth()
        self.assertEqual(self.M2E.tdcTime, 100.0)  # in us
        self.M2E.getAttribute.assert_called_once_with("", './dir/dir/dir/dir',
                                                      'pul_TDCGate',
                                                      'pulse width (ms)',
                                                      float)

        self.M2E.setTdcGateWidth(200.0)
        self.assertEqual(self.M2E.tdcTime, 200.0)

    def test_genFreqList(self):
        self.M2E.getAttribute = mock.MagicMock(return_value=
                                               "(1000000, 20, 3)")
        self.M2E.dom2ag = "dom2ag"

        result = self.M2E.genFreqList()
        expected = [999980.0, 1000000.0, 1000020.0]
        self.assertEqual(result, expected)
        self.M2E.getAttribute.assert_called_once_with(self.M2E.dom2ag,
                                                      './dir/dir',
                                                      'Variables',
                                                      'Quad FreqList')
        self.M2E.getAttribute.reset_mock()
        self.M2E.getAttribute.side_effect = Exception
        self.M2E.stopfreq = '1000020'
        self.M2E.startfreq = '999980'
        self.M2E.numfreqsteps = '3'

        result = self.M2E.genFreqList()
        expected = [999980.0, 1000000.0, 1000020.0]
        self.assertEqual(result, expected)
