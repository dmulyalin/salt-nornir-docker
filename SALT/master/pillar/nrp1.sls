proxy:
  proxytype: nornir

hosts:
  ceos1:
    hostname: 10.0.1.4
    platform: cisco_ios
    groups: [credentials]
          
groups: 
  credentials:
    username: nornir
    password: nornir