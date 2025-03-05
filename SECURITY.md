## OceanBase Security Configuration

### Creating a Restricted OceanBase User

It's crucial to create a dedicated OceanBase user with minimal permissions for the MCP server. Never use the root account or a user with full administrative privileges.

#### 1. Create a new OceanBase user

```sql
-- Connect as root or administrator
CREATE USER 'mcp_user'@'localhost' IDENTIFIED BY 'your_secure_password';
```

#### 2. Grant minimal required permissions

Basic read-only access (recommended for exploration and analysis):
```sql
-- Grant SELECT permission only
GRANT SELECT ON your_database.* TO 'mcp_user'@'localhost';
```

Standard access (allows data modification but not structural changes):
```sql
-- Grant data manipulation permissions
GRANT SELECT, INSERT, UPDATE, DELETE ON your_database.* TO 'mcp_user'@'localhost';
```

Advanced access (includes ability to create temporary tables for complex queries):
```sql
-- Grant additional permissions for advanced operations
GRANT SELECT, INSERT, UPDATE, DELETE, CREATE TEMPORARY TABLES 
ON your_database.* TO 'mcp_user'@'localhost';
```

#### 3. Apply the permissions
```sql
FLUSH PRIVILEGES;
```

### Additional Security Measures

1. **Network Access**
   - Restrict the user to connecting only from localhost if the MCP server runs on the same machine
   - If remote access is needed, specify exact IP addresses rather than using wildcards

2. **Query Restrictions**
   - Consider using VIEWs to further restrict data access
   - Set appropriate `max_queries_per_hour`, `max_updates_per_hour` limits:
   ```sql
   ALTER USER 'mcp_user'@'localhost' 
   WITH MAX_QUERIES_PER_HOUR 1000
   MAX_UPDATES_PER_HOUR 100;
   ```

3. **Data Access Control**
   - Grant access only to specific tables when possible
   - Use column-level permissions for sensitive data:
   ```sql
   GRANT SELECT (public_column1, public_column2) 
   ON your_database.sensitive_table TO 'mcp_user'@'localhost';
   ```

4. **Regular Auditing**
   - Enable OceanBase audit logging for the MCP user
   - Regularly review logs for unusual patterns
   - Periodically review and adjust permissions

### Environment Configuration

When setting up the MCP server, use these restricted credentials in your environment:

```bash
OB_USER=mcp_user
OB_PASSWORD=your_secure_password
OB_DATABASE=your_database
OB_HOST=localhost
```

### Best Practices

1. **Regular Password Rotation**
   - Change the MCP user's password periodically
   - Use strong, randomly generated passwords
   - Update application configurations after password changes

2. **Permission Review**
   - Regularly audit granted permissions
   - Remove unnecessary privileges
   - Keep permissions as restrictive as possible

3. **Access Patterns**
   - Monitor query patterns for potential issues
   - Set up alerts for unusual activity
   - Maintain detailed logs of database access

4. **Data Protection**
   - Consider encrypting sensitive columns
   - Use SSL/TLS for database connections
   - Implement data masking where appropriate