# Afterclap on other platforms

Started 2026-10-09 (Matthew): the same Shorts go to TikTok, Instagram Reels and Facebook Reels, in story order, one a day.

## Accounts
| Platform | Account | Login | Status |
|---|---|---|---|
| YouTube | @afterclapstories | brand channel under the Bearing Fruit Google account | live |
| TikTok | @afterclapstories (was @matthewohair, unused) | Matthew's personal TikTok (omatthew@gmail.com) | profile set 2026-10-09: name Afterclap, avatar, bio |
| Facebook | Page "Afterclap" (ID 61595110027037), category Digital creator | Matthew's profile; in the "Matthew O'Hair" business portfolio with Bearing Fruit | created 2026-10-09; marketing emails off. Suspended 2026-10-09 ("may impersonate someone well-known"; review requested 2:15 PM CT) and restored the same afternoon ("Page Published" after the appeal), then suspended again within the hour, right after the new avatar and reel 01 went up (same reason; a fresh "Request review" offered). Reel 01 never appeared. Avatar replaced via Chrome file_upload (the browser-pane upload had come out corrupted; the old garbled profile-picture post is still on the Page, and Pages can't limit its audience) |
| Instagram | @afterclapstories | created by Matthew 2026-10-09 on his Android | Creator account (Digital creator), linked to the Afterclap Page 2026-10-09; avatar and bio set; display name Afterclap |

Bios: TikTok "Why ordinary things are the way they are. Made with AI tools, fact-checked."; Instagram "Why ordinary things are the way they are. Short, true stories, made openly with AI tools. Sources for every claim."; Facebook "Why ordinary things are the way they are. Short, true stories, made openly with AI tools."

## Posting
- Files: TikTok copies (< 30 MB, re-encoded from the masters) in /Users/matthew/Movies/Afterclap/Social/.
- TikTok and Facebook pages block the browser pane from loading files from GitHub. What works: Claude in Chrome (Matthew's Chrome, logged in as @afterclapstories) and its file_upload tool, which takes files from this repo's working copy up to 10 MB. So each Short gets a 720p copy under 10 MB (two-pass x264, ~850 kbps video, 128 kbps audio) at stories/<id>/out/<name>-tiktok-small.mp4, plus the cover as JPG.
- The Chrome window has to be visible: in a hidden window TikTok Studio uploads the file but never shows the caption form.
- TikTok 01 posted 2026-10-09 ~1:25 PM CT with the cover image, AI-generated label on, comments on; new posts sit in "Content under review" (shown as Only me) until TikTok clears them.
- Captions: the YouTube description's first lines, a short sources line, "Made openly with AI tools and a human editor.", 2-3 hashtags. Turn on TikTok's AI-generated content label (the narration is an AI voice).
- Instagram on Matthew's Android: when it's plugged into the Mac, Desktop Commander can drive it with adb (/Users/matthew/Library/Android/platform-tools/adb): screencap to see, uiautomator dump for element bounds, input tap/text. Text typed with `input text` can lose its last letter to the Samsung keyboard's word prediction; end with punctuation or check the saved value. Instagram allows only two name changes in 14 days.
- TikTok 01 cleared review: public, 104 views by 2:00 PM CT on 2026-10-09.
- Instagram 01 posted 2026-10-09 ~1:51 PM CT from the phone (adb): 1080p file pushed to the phone, cover JPG from the camera roll (grid crop moved up to keep the title), caption typed, AI label on, "Also share on" Facebook for this reel only (not "always"). It did not reach Facebook (Page suspended at the time).
- Facebook 01 posted 2026-10-09 ~3:05 PM CT from Chrome (Page composer → Reel; 720p copy, custom thumbnail = cover JPG, caption, AI label on).
- Matthew's standing OK (2026-10-09, asked for TikTok and Instagram): repost Shorts he already approved on their days without asking each time; Facebook follows the same plan. New Shorts still go to him first.
- Never post comments or replies without Matthew's OK on the exact text (2026-10-09; may become autonomous once a commenting voice is agreed).
- Facebook Page restored again (Matthew, 2026-10-10 morning). Set up the same morning: cover photo (brand/fb-cover-1640x856.jpg: drawings from Shorts 01–06 on paper with the tagline "Why ordinary things are the way they are.", made by brand/fb-cover-compose.cjs; the first try showed the jar lid cut off in Facebook's crop, so the layout was tightened); social links Instagram, YouTube and TikTok (all @afterclapstories, checked). Reel 01 never appeared, so it's reposted around 12:25 PM CT, spaced apart from the cover change. Left for Matthew: the garbled old profile picture in Photos (only he can delete it; deleting is permanent), the Page username, and an intro post.
