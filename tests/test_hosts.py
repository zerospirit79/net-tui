from textwrap import dedent

def test_parse_hosts_basic():
    from net_tui.hosts import parse_hosts

    sample = dedent("""
        # comment
        127.0.0.1   localhost
        ::1         localhost ip6-localhost
        192.168.1.10 server1.local server1
    """).strip()

    entries = parse_hosts(sample)
    assert len(entries) == 3
    assert entries[0]["ip"] == "127.0.0.1"
    assert "localhost" in entries[0]["hosts"]
    last = entries[-1]
    assert last["ip"] == "192.168.1.10"
    assert set(last["hosts"]) >= {"server1.local", "server1"}

def test_render_hosts_roundtrip():
    from net_tui.hosts import parse_hosts, render_hosts

    original = "127.0.0.1 localhostn192.168.1.10 server1"
    data = parse_hosts(original)
    text = render_hosts(data)
    again = parse_hosts(text)
    assert again == data

