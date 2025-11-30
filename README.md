# Trabalho

Gerenciador de Servidores de Minecraft e Usuários com API RESTful

Entidades:
    servidor
    servidor
    user
    user <-> servidor
    servidor -> javalinks

# User
user_id
Name
Password
Email
created_at
updated_at

# Server
server_id
name
ip
owner_id (FK)
server_properties_id (FK)
software_id (FK)
java_id (FK)
created_at
#status

# Server_Operator
server_id (FK)
user_id (FK)
permission_level
granted_at
Primary Key: (server_id, user_id)

# Software
id
name
link
version
plugins_enabled (boolean)
mods_enabled (boolean)
created_at

# Maps
id
name
description
link
created_at

# Server_Properties
id
accepts-transfers=false
allow-flight=false
broadcast-console-to-ops=true
broadcast-rcon-to-ops=true
bug-report-link=
debug=false
difficulty=easy
enable-code-of-conduct=false
enable-jmx-monitoring=false
enable-query=false
enable-rcon=false
enable-status=true
enforce-secure-profile=true
enforce-whitelist=false
entity-broadcast-range-percentage=100
force-gamemode=false
function-permission-level=2
gamemode=survival
generate-structures=true
generator-settings={}
hardcore=false
hide-online-players=false
initial-disabled-packs=
initial-enabled-packs=vanilla
level-name=world
level-seed=
level-type=minecraft\:normal
log-ips=true
management-server-enabled=false
management-server-host=localhost
management-server-port=0
management-server-secret=cUTIGB4vlf0xTzcIMWMJvEvmCRQV4qBWNfgqKHsl
management-server-tls-enabled=true
management-server-tls-keystore=
management-server-tls-keystore-password=
max-chained-neighbor-updates=1000000
max-players=20
max-tick-time=60000
max-world-size=29999984
motd=A Minecraft Server
network-compression-threshold=256
online-mode=true
op-permission-level=4
pause-when-empty-seconds=-1
player-idle-timeout=0
prevent-proxy-connections=false
query.port=25565
rate-limit=0
rcon.password=
rcon.port=25575
region-file-compression=deflate
require-resource-pack=false
resource-pack=
resource-pack-id=
resource-pack-prompt=
resource-pack-sha1=
server-ip=
server-port=25565
simulation-distance=10
spawn-protection=16
status-heartbeat-interval=0
sync-chunk-writes=true
text-filtering-config=
text-filtering-version=0
use-native-transport=true
view-distance=10
white-list=false
