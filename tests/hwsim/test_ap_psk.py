# WPA2-Personal tests
# Copyright (c) 2014, Qualcomm Atheros, Inc.
#
# This software may be distributed under the terms of the BSD license.
# See README for more details.

import logging
logger = logging.getLogger()

import hostapd
import hwsim_utils

def test_ap_wpa2_psk(dev, apdev):
    """WPA2-PSK AP with PSK instead of passphrase"""
    ssid = "test-wpa2-psk"
    passphrase = 'qwertyuiop'
    psk = '602e323e077bc63bd80307ef4745b754b0ae0a925c2638ecd13a794b9527b9e6'
    params = hostapd.wpa2_params(ssid=ssid)
    params['wpa_psk'] = psk
    hapd = hostapd.add_ap(apdev[0]['ifname'], params)
    key_mgmt = hapd.get_config()['key_mgmt']
    if key_mgmt.split(' ')[0] != "WPA-PSK":
        raise Exception("Unexpected GET_CONFIG(key_mgmt): " + key_mgmt)
    dev[0].connect(ssid, raw_psk=psk, scan_freq="2412")
    dev[1].connect(ssid, psk=passphrase, scan_freq="2412")

def test_ap_wpa2_psk_file(dev, apdev):
    """WPA2-PSK AP with PSK from a file"""
    ssid = "test-wpa2-psk"
    passphrase = 'qwertyuiop'
    psk = '602e323e077bc63bd80307ef4745b754b0ae0a925c2638ecd13a794b9527b9e6'
    params = hostapd.wpa2_params(ssid=ssid, passphrase=passphrase)
    params['wpa_psk_file'] = 'hostapd.wpa_psk'
    hostapd.add_ap(apdev[0]['ifname'], params)
    dev[1].connect(ssid, psk="very secret", scan_freq="2412", wait_connect=False)
    dev[2].connect(ssid, raw_psk=psk, scan_freq="2412")
    dev[2].request("REMOVE_NETWORK all")
    dev[0].connect(ssid, psk="very secret", scan_freq="2412")
    dev[0].request("REMOVE_NETWORK all")
    dev[2].connect(ssid, psk="another passphrase for all STAs", scan_freq="2412")
    dev[0].connect(ssid, psk="another passphrase for all STAs", scan_freq="2412")
    ev = dev[1].wait_event(["WPA: 4-Way Handshake failed"], timeout=10)
    if ev is None:
        raise Exception("Timed out while waiting for failure report")
    dev[1].request("REMOVE_NETWORK all")

def test_ap_wpa_ptk_rekey(dev, apdev):
    """WPA-PSK/TKIP AP and PTK rekey enforced by station"""
    ssid = "test-wpa-psk"
    passphrase = 'qwertyuiop'
    params = hostapd.wpa_params(ssid=ssid, passphrase=passphrase)
    hostapd.add_ap(apdev[0]['ifname'], params)
    dev[0].connect(ssid, psk=passphrase, wpa_ptk_rekey="1", scan_freq="2412")
    ev = dev[0].wait_event(["WPA: Key negotiation completed"])
    if ev is None:
        raise Exception("PTK rekey timed out")
    hwsim_utils.test_connectivity(dev[0].ifname, apdev[0]['ifname'])
