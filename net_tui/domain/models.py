  from dataclasses import dataclass, field
  from typing import List, Optional

  @dataclass
  class InterfaceConfig:
    name: str
    state: str = "UNKNOWN"
    dhcp_v4: bool = True
    ipv4: List[str] = field(default_factory=list)
    gateway4: Optional[str] = None
    dns: List[str] = field(default_factory=list)
    search: List[str] = field(default_factory=list)
  

