from beanie import Document, Link
from beanie.odm.fields import PydanticObjectId
from pydantic import Field
from pydantic import BaseModel
from datetime import datetime

class ServersProperties(Document):
    accepts_transfers: bool = Field(default=False)
    allow_flight: bool = Field(default=False)
    broadcast_console_to_ops: bool = Field(default=True)
    broadcast_rcon_to_ops: bool = Field(default=True)
    bug_report_link: str = Field(default="")
    debug: bool = Field(default=False)
    difficulty: str = Field(default="easy")    
    enable_code_of_conduct: bool = Field(default=False)
    enable_jmx_monitoring: bool = Field(default=False)
    enable_query: bool = Field(default=False)
    enable_rcon: bool = Field(default=False)
    enable_status: bool = Field(default=True)
    enforce_secure_profile: bool = Field(default=True)
    enforce_whitelist: bool = Field(default=False)
    entity_broadcast_range_percentage: int = Field(default=100)
    force_gamemode: bool = Field(default=False)
    function_permission_level: int = Field(default=2)
    gamemode: str = Field(default="survival")
    generate_structures: bool = Field(default=True)
    generator_settings: str = Field(default="{}")
    hardcore: bool = Field(default=False)
    hide_online_players: bool = Field(default=False)
    initial_disabled_packs: str = Field(default="")
    initial_enabled_packs: str = Field(default="vanilla")
    level_name: str = Field(default="world", max_length=100)
    level_seed: str = Field(default="")
    level_type: str = Field(default="minecraft:normal")
    log_ips: bool = Field(default=True)
    management_server_enabled: bool = Field(default=False)
    management_server_host: str = Field(default="localhost")
    management_server_port: int = Field(default=0)
    max_chained_neighbor_updates: int = Field(default=1000000, ge=1)
    max_players: int = Field(default=20, ge=1, le=2147483647)
    max_tick_time: int = Field(default=60000)
    max_world_size: int = Field(default=29999984)
    motd: str = Field(default="A Minecraft Server")
    network_compression_threshold: int = Field(default=256)
    online_mode: bool = Field(default=True)
    op_permission_level: int = Field(default=4)
    pause_when_empty_seconds: int = Field(default=-1)
    player_idle_timeout: int = Field(default=0, ge=0)
    prevent_proxy_connections: bool = Field(default=False)
    query_port: int = Field(default=25565)
    rate_limit: int = Field(default=0)
    rcon_password: str = Field(default="")
    rcon_port: int = Field(default=25575)
    region_file_compression: str = Field(default="deflate")
    require_resource_pack: bool = Field(default=False)
    resource_pack: str = Field(default="")
    resource_pack_id: str = Field(default="")
    resource_pack_prompt: str = Field(default="")
    resource_pack_sha1: str = Field(default="")
    server_ip: str = Field(default="")
    server_port: int = Field(default=25565)
    simulation_distance: int = Field(default=10)
    spawn_protection: int = Field(default=16)
    status_heartbeat_interval: int = Field(default=0)
    sync_chunk_writes: bool = Field(default=True)
    text_filtering_config: str = Field(default="")
    text_filtering_version: int = Field(default=0)
    use_native_transport: bool = Field(default=True)
    view_distance: int = Field(default=10)
    white_list: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "server_properties"
        indexes = [
            "level_name",
            "gamemode",
            "difficulty",
        ]

class ServerPropertiesCreate(BaseModel):
    level_name: str = Field(..., max_length=100)
    gamemode: str = Field(default="survival")
    difficulty: str = Field(default="easy")
    max_players: int = Field(default=20, ge=1, le=10000000)
    motd: str = Field(default="A Minecraft Server", max_length=100)
