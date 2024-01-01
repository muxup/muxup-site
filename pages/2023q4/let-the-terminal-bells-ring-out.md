+++
published = 2023-12-24
description = "Once properly configured, terminal bells can be very helpful for generating simple notifications"
+++

# Let the (terminal) bells ring out

I just wanted to take a few minutes to argue that the venerable terminal bell
is a helpful and perhaps overlooked tool for anyone who does a lot of their
work out of a terminal window. First, an important clarification. Bells
ringing, chiming, or (as is appropriate for the season) jingling all sounds
very noisy - but although you can configure your terminal emulator to emit a
sound for the terminal bell, I'm actually advocating for configuring a
non-intrusive but persistent visual notification.

## BEL

Our goal is to generate a visual indicator on demand (e.g. when a long-running
task has finished) and to do so with minimal fuss. This should work over ssh
and without worrying about forwarding connections to some notification
daemon. The ASCII `BEL` control character (alternatively written as `BELL` by
those willing to spend characters extravagantly) meets these requirements.
You'll just need co-operation from your terminal emulator and window manager
to convert the bell to an appropriate notification.

`BEL` is `7` in ASCII, but can be printed using `\a` in `printf` (including
the `/usr/bin/printf` you likely use from your shell, [defined in
POSIX](https://pubs.opengroup.org/onlinepubs/9699919799/utilities/printf.html)).
There's even a [Rosetta Code
page](https://rosettacode.org/wiki/Terminal_control/Ringing_the_terminal_bell)
on ringing the terminal bell from various languages. Personally, I like to
define a shell alias such as:

```sh
alias bell="printf '\aBELL!\n'"
```

Printing some text alongside the bell is helpful for confirming the bell was
triggered as expected even after it was dismissed. Then, if kicking off a long
operation like an LLVM compile and test use something like:

```sh
cmake --build . && ./bin/llvm-lit -s test; bell
```

The `;` ensures the bell is produced regardless of the exit code of the
previous commands. All being well, this sets the urgent hint on the X11 window
used by your terminal, and your window manager produces a subtle but
persistent visual indicator that is dismissed after you next give focus to the
source of the bell. Here's how it looks for me in
[DWM](https://dwm.suckless.org/):

![Screenshot of DWM showing a notification from a
bell](/static/bell_example.png "DWM screenshot")

The above example shows 9 workspaces (some of them named), where the `llvm`
workspace has been highlighted because a bell was produced there. You'll also
spot that I have a `timers` workspace, which I tend to use for miscellaneous
timers. e.g. a reminder before a meeting is due to start, or when I'm planning
to switch a task. I have a small tool for this I might share in a future post.

A limitation versus triggering [freedesktop.org Desktop
Notifications](https://specifications.freedesktop.org/notification-spec/latest/)
is that there's no payload / associated message. For me this isn't a big deal,
such messages are distracting, and it's easy enough to see the full context
when switching workspaces. It's possible it's a problem for your preferred
workflow of course.

You _could_ put `\a` in your terminal prompt (`$PS1`), meaning a bell is
triggered after every command finishes. For me this would lead to too many
notifications for commands I didn't want to carefully monitor the output for,
but your mileage may vary. After publishing this article, my
[Igalia](https://igalia.com) colleague Adrian Perez pointed me to a slight
variant on this that he uses: in Zsh `$TTYIDLE` makes it easy to configure
behaviour based on the duration of a command and [he configures zsh so a bell
is produced for commands that take longer than 30
seconds to
complete](https://github.com/aperezdc/dotfiles/blob/ce6a240bcbcac7b796895da581f0a6c5f23f31d5/dot.zsh--rc.zsh#L392).

## Terminal emulator support

Unfortunately, setting the urgent hint upon a bell is not supported by
gnome-terminal, with a [15 year-old issue left
unresolved](https://gitlab.gnome.org/GNOME/gnome-terminal/-/issues/6698). It
is however supported by the otherwise very similar xfce4-terminal (just enable
the visual bell in preferences), and I switched solely due to this issue.

From what I can tell, this is the status of visual bell support via setting
the X11 urgent hint:
* xfce4-terminal: Supported. In Preferences -> Advanced ensure "Visual bell"
  is ticked.
* xterm: Set `XTerm.vt100.bellIsUrgent: true` in your `.Xresources` file.
* rxvt-unicode (urxvt): Set `URxvt.urgentOnBell: true` in your `.Xresources`
  file.
* alacritty: Supported. Works out of the box with no additional configuration
  needed.
* gnome-terminal: [Not
  supported](https://gitlab.gnome.org/GNOME/gnome-terminal/-/issues/6698).
* konsole: As far as I can tell it isn't supported. Creating a new profile and
  setting the "Terminal bell mode" to "Visual Bell" doesn't seem to result in
  the urgent hint being set.

## Article changelog
* 2023-12-24: (minor) Add note about configuring a bell for commands taking
  longer than a certain threshold duration in Zsh.
