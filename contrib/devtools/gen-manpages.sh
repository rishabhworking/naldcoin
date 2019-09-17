#!/bin/sh

TOPDIR=${TOPDIR:-$(git rev-parse --show-toplevel)}
SRCDIR=${SRCDIR:-$TOPDIR/src}
MANDIR=${MANDIR:-$TOPDIR/doc/man}

NALDD=${NALDD:-$SRCDIR/naldd}
NALDCLI=${NALDCLI:-$SRCDIR/nald-cli}
NALDTX=${NALDTX:-$SRCDIR/nald-tx}
NALDQT=${NALDQT:-$SRCDIR/qt/nald-qt}

[ ! -x $NALDD ] && echo "$NALDD not found or not executable." && exit 1

# The autodetected version git tag can screw up manpage output a little bit
NALDVER=($($NALDCLI --version | head -n1 | awk -F'[ -]' '{ print $6, $7 }'))

# Create a footer file with copyright content.
# This gets autodetected fine for naldd if --version-string is not set,
# but has different outcomes for nald-qt and nald-cli.
echo "[COPYRIGHT]" > footer.h2m
$NALDD --version | sed -n '1!p' >> footer.h2m

for cmd in $NALDD $NALDCLI $NALDTX $NALDQT; do
  cmdname="${cmd##*/}"
  help2man -N --version-string=${NALDVER[0]} --include=footer.h2m -o ${MANDIR}/${cmdname}.1 ${cmd}
  sed -i "s/\\\-${NALDVER[1]}//g" ${MANDIR}/${cmdname}.1
done

rm -f footer.h2m
