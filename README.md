# Guantlet
Discord bot to create custom tourneys for ELO character ranking with a little bit of flair ✨.

### Yap Bot
A bot that sends automated pings every X minutes.

Ensure that:
1. `Allow anyone to @mention this role` is enabled for the desired role.
2. `Mention @everyone, @here, and All Roles` is enabled for the bot.

**Future Improvements:**
- ✅ Persistence: Store active reminders in a database so they survive bot restarts.
- ✅ Multiple channels support: Allow specifying a channel when starting a reminder.
- ✅ Admin-only commands: Restrict yap commands to admins using `@commands.has_permissions(administrator=True)`.

## Local Development

```bash
bash scripts/setup_env.sh
```

### Precommit
Apply formatter, linter, type checker, etc.

```bash
bash scripts/precommit.sh
```

## Discord
Create the Discord app by following the "Getting Started" guide [here](https://discord.com/developers/docs/quick-start/getting-started).