from sqlmodel import SQLModel, Field

class ServerProperties(SQLModel, table=True):
    __tablename__ = "server_properties"
    # Basic server settings
    id: int = Field(default=None, primary_key=True)
    accepts_transfers: bool = False
    allow_flight: bool = False
    broadcast_console_to_ops: bool = True
    broadcast_rcon_to_ops: bool = True
    bug_report_link: str = ""
    debug: bool = False
    difficulty: str = "easy"
    
    # Feature toggles
    enable_code_of_conduct: bool = False
    enable_jmx_monitoring: bool = False
    enable_query: bool = False
    enable_rcon: bool = False
    enable_status: bool = True
    enforce_secure_profile: bool = True
    enforce_whitelist: bool = False
    
    # Game settings
    entity_broadcast_range_percentage: int = 100
    force_gamemode: bool = False
    function_permission_level: int = 2
    gamemode: str = "survival"
    generate_structures: bool = True
    generator_settings: str = "{}"
    hardcore: bool = False
    hide_online_players: bool = False
    
    # World settings
    initial_disabled_packs: str = ""
    initial_enabled_packs: str = "vanilla"
    level_name: str = "world"
    level_seed: str = ""
    level_type: str = "minecraft:normal"
    
    # Network and security
    log_ips: bool = True
    management_server_enabled: bool = False
    management_server_host: str = "localhost"
    management_server_port: int = 0
    
    # Performance settings
    max_chained_neighbor_updates: int = 1000000
    max_players: int = 20
    max_tick_time: int = 60000
    max_world_size: int = 29999984
    
    # Server info
    motd: str = "A Minecraft Server"
    network_compression_threshold: int = 256
    online_mode: bool = True
    op_permission_level: int = 4
    
    # Timeouts and limits
    pause_when_empty_seconds: int = -1
    player_idle_timeout: int = 0
    prevent_proxy_connections: bool = False
    
    # Ports and connections
    query_port: int = 25565
    rate_limit: int = 0
    rcon_password: str = ""
    rcon_port: int = 25575
    
    # File and resource settings
    region_file_compression: str = "deflate"
    require_resource_pack: bool = False
    resource_pack: str = ""
    resource_pack_id: str = ""
    resource_pack_prompt: str = ""
    resource_pack_sha1: str = ""
    
    # Server network
    server_ip: str = ""
    server_port: int = 25565
    
    # World rendering
    simulation_distance: int = 10
    spawn_protection: int = 16
    status_heartbeat_interval: int = 0
    sync_chunk_writes: bool = True
    
    # Text filtering
    text_filtering_config: str = ""
    text_filtering_version: int = 0
    
    # Transport
    use_native_transport: bool = True
    view_distance: int = 10
    white_list: bool = False
