
Debian
====================
This directory contains files used to package naldd/nald-qt
for Debian-based Linux systems. If you compile naldd/nald-qt yourself, there are some useful files here.

## nald: URI support ##


nald-qt.desktop  (Gnome / Open Desktop)
To install:

	sudo desktop-file-install nald-qt.desktop
	sudo update-desktop-database

If you build yourself, you will either need to modify the paths in
the .desktop file or copy or symlink your nald-qt binary to `/usr/bin`
and the `../../share/pixmaps/nald128.png` to `/usr/share/pixmaps`

nald-qt.protocol (KDE)

