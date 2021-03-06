
from __future__ import absolute_import

import re
import muz
import muz.beatmap

extensions = ["osu"]
locations = ["beatmaps"]

patternSection = re.compile(r'^\[([a-zA-Z0-9]+)\]$')
patternKeyVal = re.compile(r'^([a-zA-Z0-9]+)\s*:\s*(.*)$')

def read(fobj):
    buf = ""
    bmap = muz.beatmap.Beatmap(None, 1)
    versionOk = False
    section = None

    while True:
        byte = fobj.read(1)

        if not byte:
            break

        if byte in ('\r', '\n'):
            buf = buf.decode('utf-8').strip()

            if not buf or  buf.startswith("//"):
                buf = ""
                continue

            if not versionOk:
                assert "osu file format v" in buf
                versionOk = True
                buf = ""
                continue

            s = patternSection.findall(buf)
            if s:
                section = s[0]
                buf = ""
                continue

            if section == "Events" or section == "TimingPoints":
                buf = ""
                continue
            elif section == "HitObjects":
                vals = buf.split(',')
                hit = int(vals[2])
                hold = 0

                if int(vals[3]) & 128:
                    hold = int(vals[5].split(":")[0]) - hit

                # "human-readable" my ass
                # let's hope there is no beatmap that sets "CircleSize" AFTER the HitObjects section
                band = int(int(vals[0]) / (512 / bmap.numbands))

                # maybe CircleSize lied to us...
                bmap.numbands = max(bmap.numbands, band + 1)

                bmap.append(muz.beatmap.Note(band, hit, hold))

                buf = ""
                continue
            else:
                s = patternKeyVal.findall(buf)
                if s:
                    key, val = s[0]

                    if section == "General":
                        if key == "AudioFilename":
                            bmap.music = val.replace("\\", "/")
                    elif section == "Difficulty":
                        if key == "CircleSize":
                            bmap.numbands = int(float(val))

                    bmap.meta["osu.%s.%s" % (section, key)] = val
                    buf = ""
                    continue

            raise SyntaxError("failed to parse %s in an osu! beatmap" % repr(buf))

        buf += byte

    bmap.meta["Music.Name"] = bmap.meta["osu.Metadata.TitleUnicode"]
    bmap.meta["Music.Name.ASCII"] = bmap.meta["osu.Metadata.Title"]

    bmap.meta["Music.Artist"] = bmap.meta["osu.Metadata.ArtistUnicode"]
    bmap.meta["Music.Artist.ASCII"] = bmap.meta["osu.Metadata.Artist"]

    bmap.meta["Beatmap.Variant"] = bmap.meta["osu.Metadata.Version"]
    bmap.meta["Beatmap.Author"] = bmap.meta["osu.Metadata.Creator"]

    bmap.applyMeta()
    return bmap
