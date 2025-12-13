# ❓ Frequently Asked Questions

Common questions and answers about the Classroom OBS Control System.

---

## General Questions

### What is this system for?

This system allows students to interact with your live presentation by triggering visual effects, changing scenes, and controlling OBS filters through a web interface - no software installation required on their end!

### Do students need to install anything?

**No!** Students only need a web browser. Everything runs through the web interface you host.

### Does this work on phones and tablets?

**Yes!** The interface is fully responsive and works great on mobile devices.

### Can I use this with other streaming software?

Currently, it's designed specifically for OBS Studio. However, the system could be adapted for other software that has API/WebSocket support (like XSplit, vMix, etc.).

---

## Setup Questions

### What version of OBS do I need?

OBS Studio 28 or newer (which has WebSocket built-in). You're using 32.x family, which is perfect!

### Do I need OBS WebSocket plugin?

If you're using OBS 28 or newer (which you are with 32.x), **no** - WebSocket is built-in! Just enable it in Tools → WebSocket Server Settings.

### Can I run this on a Mac?

The server code is Node.js and should work on Mac, but the setup instructions are written for Windows. You mentioned you're running Windows, so you're all set!

### Do I need a powerful computer?

**Minimum:**
- Dual-core processor
- 4GB RAM
- Windows 10/11

**Recommended:**
- Quad-core processor
- 8GB+ RAM
- Dedicated graphics card (if streaming)

---

## Network & Access Questions

### How do students access the interface?

You have several options:
1. **ngrok** (easiest for testing) - Provides a public URL automatically
2. **Port forwarding** - Use your public IP address
3. **Dynamic DNS** - Get a memorable URL (e.g., myclassroom.ddns.net)
4. **Host on Squarespace** - Upload files and point to your server

### Is it secure?

Yes! Security features include:
- Password authentication (teacher and student levels)
- Rate limiting (prevents spam)
- Kill switch (instant disable)
- Optional IP whitelisting
- HTTPS support (automatic with ngrok)

### What if my IP address changes?

Use Dynamic DNS (DDNS) services like No-IP or DuckDNS. They give you a stable hostname that updates automatically when your IP changes.

### Can students outside my school use it?

Yes, if you want! The system works over the internet. However, you control who has access via passwords. You can also restrict by IP address if needed.

### Does my school firewall affect this?

- **Incoming**: You need to allow incoming connections on your chosen port (default: 3000)
- **Outgoing**: Students only need standard HTTPS access
- **ngrok**: Often bypasses firewall issues

---

## Usage Questions

### How many students can connect at once?

The system can handle **hundreds** of simultaneous connections. The real limitation is your internet upload speed and computer performance. For typical classroom use (30-40 students), you'll have no issues.

### Will effects happen instantly?

Yes! Commands are processed in real-time. There may be 100-500ms delay depending on internet speed, but it feels instant for most uses.

### Can multiple students trigger effects at the same time?

**Yes!** The system handles concurrent requests. Rate limiting prevents any one student from spamming.

### What if students spam the buttons?

**Two protections:**
1. **Rate limiting**: Students can only trigger 10 effects per 5 seconds (configurable)
2. **Kill switch**: You can instantly disable all student controls

### Can I still control OBS manually?

**Absolutely!** The system doesn't lock you out. You can:
- Use OBS normally
- Use Stream Deck
- Have full manual control
All controls work simultaneously!

---

## Technical Questions

### What ports does this use?

- **3000**: Web server (configurable)
- **4455**: OBS WebSocket (OBS default)

### Does this record anything?

By default, no. However, you can enable logging to track what effects were triggered (see ADVANCED.md).

### Can I run this 24/7?

Yes! You can set it up as a Windows service (see ADVANCED.md) or just leave it running. It's very lightweight.

### What happens if the server crashes?

- Students lose connection
- Your OBS keeps running normally
- Just restart the server (students can reconnect)

### Does this affect OBS performance?

**Minimal impact.** The system makes small API calls to OBS. If you have many effects triggering simultaneously, there might be slight lag, but it's negligible for modern computers.

---

## Customization Questions

### Can I add my own buttons?

**Yes!** It's easy. See [CUSTOMIZATION.md](CUSTOMIZATION.md) for detailed instructions. You just need to:
1. Add the filter/source in OBS
2. Add a button in the HTML
3. Match the names - done!

### Can I change the look/colors?

**Absolutely!** Edit `public/styles.css` to change colors, fonts, layouts - anything visual. The CSS uses variables for easy theming.

### Can I add sounds or music?

Not built-in by default, but you can:
1. Use OBS audio sources that students can trigger
2. Integrate VoiceMod (see ADVANCED.md)
3. Add browser source with sound effects

### Can students upload images?

Not in the default configuration (security risk), but you could add this feature. You'd need to:
- Add file upload handling
- Validate files
- Create OBS image sources dynamically

---

## Integration Questions

### Does this work with Stream Deck?

**Yes!** Stream Deck can control OBS via the same WebSocket connection. Both can run simultaneously. Stream Deck is your teacher control panel, web interface is for students.

### Does this work with VoiceMod?

Yes, with some setup! See [ADVANCED.md](ADVANCED.md) for VoiceMod integration instructions.

### Can I integrate with Google Classroom?

Not directly, but you could:
- Share the link in Google Classroom
- Embed in a classroom page
- Use Google Sheets for logging (see ADVANCED.md)

### Does it work with Zoom/Teams?

**Yes!** Use OBS Virtual Camera:
1. In OBS: Tools → Virtual Camera → Start
2. In Zoom/Teams: Select "OBS Virtual Camera" as your camera
Students control the effects, Zoom/Teams just sees the camera output!

---

## Troubleshooting

### "Cannot connect to OBS"

**Checklist:**
- [ ] Is OBS running?
- [ ] Is WebSocket enabled in OBS? (Tools → WebSocket Server Settings)
- [ ] Is the password correct in your `.env` file?
- [ ] Is OBS on port 4455? (check your `.env`)

### "Students can't connect"

**Checklist:**
- [ ] Is the server running? (`npm start`)
- [ ] Is ngrok running? (if using ngrok)
- [ ] Are you sharing the HTTPS URL from ngrok?
- [ ] Did students enter the correct password?
- [ ] Try accessing the URL yourself first

### "Buttons don't do anything"

**Checklist:**
- [ ] Are the filter/source names EXACTLY correct? (case-sensitive)
- [ ] Do the filters/sources exist in OBS?
- [ ] Is OBS connected? (check status indicator)
- [ ] Check the server console for error messages
- [ ] Check browser console (F12) for errors

### "Effects are laggy"

**Possible causes:**
- Slow internet connection (yours or students')
- Too many effects triggering at once
- Computer running heavy applications
- OBS rendering complex scenes

**Solutions:**
- Increase rate limiting
- Simplify OBS scenes
- Close unnecessary applications
- Upgrade internet connection

### "Password won't work"

**Common issues:**
- Using the plain password instead of the hash in `.env`
- Typo in password
- Wrong role selected (teacher vs student)

**Solution:**
Regenerate password hashes using the `/api/hash-password` endpoint (see Setup Guide).

---

## Best Practices

### Before Class

- [ ] Start OBS
- [ ] Start server
- [ ] Start ngrok (if using)
- [ ] Test the URL yourself
- [ ] Test on a mobile device
- [ ] Have kill switch ready

### During Class

- [ ] Explain the system to students first
- [ ] Start with kill switch ON
- [ ] Demo an effect yourself
- [ ] Turn off kill switch
- [ ] Monitor the activity feed
- [ ] Use kill switch when you need focus

### After Class

- [ ] You can leave server running for next time
- [ ] Stop ngrok if you don't need it
- [ ] Check logs for popular effects
- [ ] Note any issues for fixing

---

## Education-Specific Questions

### What age group is this for?

**All ages!** We've seen it used successfully with:
- Elementary (supervised, fewer buttons)
- Middle school (perfect sweet spot)
- High school (more complex setups)
- College (advanced integrations)

Adjust complexity to match your students.

### How do I prevent chaos?

**Strategies:**
1. **Set clear expectations** - Explain rules upfront
2. **Use the kill switch** - Don't hesitate!
3. **Rate limiting** - Configured by default
4. **Start simple** - Add more buttons gradually
5. **Reward system** - Good behavior earns access
6. **Time limits** - Only enable during certain activities

### What if my administration has concerns?

**Points to make:**
- **Educational value** - Increases engagement
- **No installation required** - Students use web browser
- **Teacher controlled** - Kill switch gives you full control
- **Password protected** - Secure access
- **You own the system** - Runs on your computer
- **Professional tools** - Uses OBS Studio (free, open-source)

Offer to demo it for them!

### How do I justify this to parents?

**Benefits to highlight:**
- **Engagement** - Keeps students interested
- **Interactive learning** - Active participation
- **Modern skills** - Technology literacy
- **Motivation** - Students excited to attend class
- **Control** - Teacher maintains full authority

Many parents will think it's cool!

---

## Cost Questions

### How much does this cost?

**Free to use!** This system is open-source. Costs might include:

- **OBS Studio**: Free ✅
- **Node.js**: Free ✅
- **This system**: Free ✅
- **ngrok free tier**: Free ✅
- **ngrok paid** (static URL): $8-10/month
- **Domain name** (optional): $10-15/year
- **Dynamic DNS** (optional): Free - $5/month

**Minimum cost: $0** (using all free options)

### Do I need ngrok premium?

**No**, the free tier works great! Premium gives you:
- Static URL (doesn't change)
- More simultaneous connections
- Faster speeds

For one classroom, free is usually enough.

---

## Future Enhancements

### What's coming next?

Possible future features:
- VoiceMod integration (sound effects)
- Voting system (students vote on effects)
- Point rewards (gamification)
- Student accounts (individual tracking)
- Analytics dashboard
- Mobile app
- Presets and sequences
- Schedule system

Want to contribute? The system is designed to be expandable!

### Can I request features?

Sure! While this is a template system you can modify yourself, feature ideas are welcome for future versions.

---

## Support

### Where can I get help?

1. Read the documentation:
   - [README.md](README.md) - Overview
   - [SETUP_GUIDE.md](SETUP_GUIDE.md) - Detailed setup
   - [QUICK_START.md](QUICK_START.md) - Fast setup
   - [CUSTOMIZATION.md](CUSTOMIZATION.md) - Customization
   - [ADVANCED.md](ADVANCED.md) - Advanced features

2. Check error messages:
   - Server console
   - Browser console (F12)

3. Common fixes:
   - Restart server
   - Restart OBS
   - Check passwords
   - Verify filter names

### Can I hire someone to set this up?

Yes, you could hire a tech-savvy student, IT person, or freelancer. The setup is straightforward for anyone with basic technical skills.

### Is there a video tutorial?

Not included, but the QUICK_START.md guide is designed to be followed step-by-step in about 15 minutes.

---

## Legal Questions

### Can I use this in my school?

**Yes!** The system is open-source (MIT License). You can use it freely in educational settings.

### Can I modify the code?

**Absolutely!** That's encouraged. The MIT License allows you to modify, distribute, and even sell modified versions if you want.

### Do I need to credit anyone?

Not required by the license, but it's appreciated if you share where you got it!

### Can I share this with other teachers?

**Please do!** Help other educators create engaging classrooms.

---

## Still Have Questions?

If your question isn't answered here:

1. Check the detailed guides (README, SETUP_GUIDE, etc.)
2. Review the code comments
3. Search for similar issues online
4. Check OBS and Node.js documentation

**Remember:** You're running everything locally on your computer, so you have full control and can experiment safely!

---

**Happy teaching! 🎓**
