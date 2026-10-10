save_editor.py opens a very basic save editor for 雷电皇 比卡丘传说 (Lei Dian Huang Bi Ka Qiu Chuan Shuo).
you need Python to use this, and it only edits the Pokémon in the party.
i haven't tested every single move and species, so back up your save file before using it.
i won't take responsibility if you forget to do it.

the slot display order of the party Pokémon may vary due to how the game shifts records but it shouldn't affect usage.
if there isn't 6 Pokémon in the party, the editor will refuse to open (safety feature to avoid editing PC).
don't do weird things like making the first move empty or it'll get stuck using Tackle.

i've only used this with the original Chinese version.
i don't use patches for the game, so if you're using some translation patch, i can't guarantee compatibility.
the editor displays in English, but you can edit the names in speciesIndex and moveIndex to translate to other languages.

when editing moves, the current number of Power Points (PP) in them won't be edited.
because of this, they can end up higher than the maximum PP for the new move.
but this shouldn't cause problems, and using the move enough or healing at the PokéCen will fix it.
if the level or species is changed, the stats won't update immediately, so level up the Pokémon to update it.

for the Pokédex and item scripts, you need to manually edit in the input and output file names.
put the save file to edit in the same directory and edit the name into the py file.
with the Pokédex script, entries numbered 157-159 will be artifically labelled as caught to reveal the Pokémon's descriptions (see comments for how to remove this).

Kyogre, Groudon, and Rayquaza can't normally be obtained, but you can edit them in if you want.
i didn't add Missingno (looks like a "?") to the editor because it's not friendly (breaks the game).
<br><hr><br>
Credits:<br>
checksum logic is followed from Inkbox on YouTube.
they made the getRareCandy.py, i adapted it for some other items.
i also used their <a href="https://www.youtube.com/watch?v=WJmAl2DNvU8">video</a> as a base for the completePokedex.py.
i improved upon it by referencing my save file that was completed naturally, so it should now properly flag captured entries.

i used the English names and move indexes from a spreadsheet by "Kingpepe".
English isn't my first language so if you don't know what the moves do, you can <a href="https://docs.google.com/spreadsheets/d/16a-fot8BFq7Q11ahwKa7js8pkC8aGfxMHlWW0AK9koY/edit?gid=1053279941#gid=1053279941">go look at it</a>.

it's not hard to expand these tools but i don't have the time, so feel free to take them and make them better.