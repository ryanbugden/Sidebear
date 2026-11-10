<img src="source/resources/mechanic_icon.png"  width="80">

# Sidebear


A RoboFont extension for quickly manipulating your glyph’s sidebearings. 

Sidebear installs itself in your Inspector, underneath the Glyph Info pane.
<br />
<br />



## Actions include:
`Enter Desired SB` You may enter numerical values or glyph names. If you place a comma `,` before or after the glyph name, the opposite SB will be matched (e.g. `,n` input on the LSB of glyph `u`  will match the RSB of the `n`.). Also, like the native Glyph panel, you can input glyph math (e.g. `(H + O)/2 + 2`)
<br />
`Swap SBs`
<br /><br />
`Make LSB = RSB`
<br />
`Center glyph` Make SBs equal (Set width may change ± 1)
<br />
`Make RSB = LSB`

##### Choose an increment, then:
`Contract both SBs` equally by that increment.
<br />
`Expand both SBs` equally by that increment.
<br /><br /><br />


<hr />
ʕ·ᴥ· ʔ
<br />
Enjoy designing with your friendly Sidebear.

Special thanks to Just van Rossum, Gustavo Ferreira, Frederik Berlaen, Frank Griesshammer, Erik van Blokland, Colin Ford
<br />

### Versions

```
2.0:   2023.10.23  Support glyph math (e.g. H+10). Sleeker UI, legible in dark mode. 
1.1.6: 2023.05.31  Refined Mechanic icon
1.1.5: 2022.03.01  Sidebear keeps your last increment, and shows the right SB info immediately upon open. Attempted updating to Subscriber, but decided unnecessary!
1.1.1: 2020.03.16  Implemented "rounding" for more predictable results, optimized code, removed print statements
1.1.0: 2020.03.03  Support for italic angles. Thanks for the note, Colin Ford!
1.0.5: 2020.01.24
1.0.4: 2019.05.07
1.0.3: 2019.04.09
1:     2019.03.28  Initial release
```

**P.S.**  If you like the idea behind Sidebear, but want to try a tool with a different approach, check out OkayType’s [here](https://github.com/okay-type/GlyphviewMetricsHUD-robofontExt).
