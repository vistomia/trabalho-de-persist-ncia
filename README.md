# trabalho

api -> infra -> db
        -> auth
        -> core

TCP

## Client API Endpoints

Testar hash

- `GET /hash/{hash_name}/{data}` - Compute hash for given data using specified hash type
- `GET /hash/md5/{data}` - Compute MD5 hash for given data
- `GET /hash/sha1/{data}` - Compute SHA1 hash for given data
- `GET /hash/sha256/{data}` - Compute SHA256 hash for given data

### Authentication

- `POST /login` - User authentication
- `POST /register` - User registration

### Server Management

- `POST /server` - Create new server with world
- `GET /server` - Get server configuration
- `PUT /server` - Update server configuration  
- `DELETE /server` - Delete server

### World Configuration

- `GET /server/world` - Get world settings
- `PUT /server/world` - Update world settings
- `DELETE /server/world` - Delete world

### Server Control

- `POST /server/start` - Start server
- `POST /server/stop` - Stop server
- `GET /server/status` - Get server status
- `GET /server/logs` - Get server logs

- `POST /server/backup` - Create server backup
- `GET /server/backup` - List server backups
- `POST /server/restore` - Restore server from backup
- `DELETE /server/backup` - Delete server backup

- `GET /server/players` - List online players

- `GET /server/operators` - List server operators
- `POST /server/operators` - Add server operator
- `DELETE /server/operators` - Remove server operator

- `POST /server/whitelist` - Add player to whitelist
- `DELETE /server/whitelist` - Remove player from whitelist
- `GET /server/whitelist` - List whitelisted players

- `POST /server/ban` - Ban player
- `DELETE /server/ban` - Unban player
- `GET /server/ban` - List banned players

- `GET /alambic/migrate` - Run database migrations 
- `POST /server/command` - Execute server command
