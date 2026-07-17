# How to Connect to a WebDAV Server Directly on macOS and Windows

This guide covers direct, built-in WebDAV connections using macOS and Windows tools. It does not require Cyberduck, Mountain Duck, or another third-party client.

## Before You Start

You will need:

- Your WebDAV server URL, such as `https://files.example.com/` or `https://files.example.com/webdav/`
- A username and password
- The correct folder path if your WebDAV share is not at the server root

Use `HTTPS` whenever possible. It protects credentials in transit and avoids several Windows authentication issues that commonly appear with plain `HTTP`.

## Method 1: Connect from Finder on macOS

This is the simplest built-in option for most Mac users.

1. Open Finder.
2. In the menu bar, choose `Go` > `Connect to Server`.
3. Enter your WebDAV address in the `Server Address` field.
   Example: `https://files.example.com/webdav/`
4. Click `Connect`.
5. Enter your username and password when prompted.
6. The WebDAV share appears in Finder under `Locations`.

To disconnect, open a Finder window and click the eject icon next to the mounted server in the sidebar.

Best for:

- Everyday Mac users
- Occasional file access
- Teams that want the most familiar macOS workflow

## Method 2: Map the WebDAV Share in File Explorer on Windows

This method makes the WebDAV location show up like a mapped drive or network location in File Explorer.

1. Open File Explorer.
2. Select `This PC`.
3. In Windows 11, choose `More` > `Map network drive`.
   In Windows 10, choose the `Computer` tab, then `Map network drive`.
4. Pick a drive letter.
5. In the folder field, enter the WebDAV URL.
   Example: `https://files.example.com/webdav/`
6. Click `Finish`.
7. Enter your username and password if Windows prompts for them.

Important Windows note:

- Microsoft lists the built-in `WebClient` WebDAV service as deprecated.
- Microsoft also says the service is not started by default.
- If mapping fails, open `services.msc`, find `WebClient`, and make sure it is enabled and running.

Best for:

- Windows users who want the share visible in File Explorer
- Repeated access to the same WebDAV location
- Workflows that expect a drive letter

## Method 3: Use the Command Line

This method is best for admins, power users, login scripts, and troubleshooting.

### macOS Terminal

Create a mount point first, then mount the share:

```bash
mkdir -p /Volumes/webdav
mount_webdav -i https://files.example.com/webdav/ /Volumes/webdav
```

Notes:

- `-i` prompts for username and password interactively.
- `mount_webdav` also supports `http://` and `https://`, but `https://` is strongly preferred.
- To unmount later, use:

```bash
umount /Volumes/webdav
```

### Windows Command Prompt

Map a WebDAV location with `net use`:

```cmd
net use Z: https://files.example.com/webdav/
```

Or let Windows choose the next available drive letter:

```cmd
net use * https://files.example.com/webdav/
```

If prompted, enter your credentials. If the command fails immediately, check that the `WebClient` service is running.

Best for:

- Scripts and automation
- Repeatable setup steps for support teams
- Troubleshooting native WebDAV issues

## Which Method Should You Recommend?

If you are writing for a mixed macOS and Windows audience, the cleanest framing is:

1. `Finder on macOS` for the easiest native Mac workflow
2. `File Explorer on Windows` for the easiest native Windows workflow
3. `Command line on either platform` for admins, automation, and troubleshooting

## Common Problems

### The URL works in a browser but not as a mounted share

Check that you are using the actual WebDAV endpoint, not just the website homepage. Many services use a path such as `/webdav/`, `/remote.php/dav/files/username/`, or another provider-specific route.

### Windows refuses to connect

Start with these checks:

- Make sure the `WebClient` service is running
- Use `HTTPS` instead of `HTTP`
- Confirm the server certificate matches the hostname you entered
- If the site is using a fully qualified domain name and Windows keeps prompting for credentials, you may need additional WebClient configuration for credential forwarding

### Authentication keeps failing

Verify:

- The username format required by your provider
- The exact folder path
- Whether the server expects an app password, token, or domain-qualified username

## Bottom Line

For most readers, the native path is straightforward:

- On macOS, use `Finder` > `Go` > `Connect to Server`
- On Windows, use `File Explorer` > `This PC` > `Map network drive`
- For advanced use, use `mount_webdav` on macOS or `net use` on Windows

## Sources

- Apple Support: [Connect to or disconnect from a WebDAV server on Mac](https://support.apple.com/guide/mac-help/connect-disconnect-a-webdav-server-mac-mchlp1546/mac)
- Microsoft Support: [File sharing over a network in Windows](https://support.microsoft.com/en-us/windows/experience/connectivity-networking/file-sharing-over-a-network-in-windows)
- Microsoft Learn: [Using the WebDAV Redirector](https://learn.microsoft.com/en-us/iis/publish/using-webdav/using-the-webdav-redirector)
- Microsoft Learn: [Deprecated features in the Windows client](https://learn.microsoft.com/en-us/windows/whats-new/deprecated-features)
- Microsoft Learn: [Prompt for credentials when you access WebDav-based FQDN sites in Windows](https://learn.microsoft.com/en-us/troubleshoot/windows-server/networking/credentials-prompt-access-webdav-fqdn-sites)
