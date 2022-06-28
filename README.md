# CHAT + BOT
---

## &mdash; (work in progress) &mdash;
(possible here will be a django project too in the future)

**I know, it's buggy, but works!**

Here I have **4** different projects at the moment.

Each project starts with a prefix.

---
### Let's see the contents:
---

BOT_*
- this `<BOT>` is trained for a few things only!
  - just to see and test, how it works if is it works...
  - unfortunately, I wasn't able to test it, but hopefully it works!
    - possible I can test it on my other machine, but I don't know when.
- you can see the "knowledge" in the json file.
- you can also extend it with your own customizations, but after that you should "train" the `<BOT>` to know those things as well.
- how to train it? just run the `python bot_training.py` and it will re-write the `*.pkl` files.
- don't forget: it requires a `tensorflow` package...
- and also a `natural language toolkit: nltk`.
- and `NumPy` as well.

GUI_*
- very simple design.
- it requires TkInter because of the client.
- after exiting: the server-side writes unwanted code...

TCP_*
- ***adminpass*** is not "hidden", no hash used. why? because you can try it yourself to be admin.
- if the command "/ban" does not work properly, try to create an empty "tcp_banned.txt" manually, and try it again.

UDP_*
- if the message is undelivered... it's UDP! it happens...

---

### MADE WITH/ON:
- Fedora GNU/Linux
- VSCodium
- Python 3.10.5
- gnome-terminal
- oh-my-zsh
- git
- gh (cli)

---
**<center>@dabzse {{ MNY }}</center>**
