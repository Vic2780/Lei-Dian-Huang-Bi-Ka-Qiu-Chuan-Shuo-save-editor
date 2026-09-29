save_editor.pyw opens a very basic save editor for 雷电皇 比卡丘传说 (Lei Dian Huang Bi Ka Qiu Chuan Shuo).
you need Python to use this, and it only edits the first Pokémon in the party.
i haven't tested every single move and species, so back up your save file before using it.
i won't take responsibility if you forget to do it.
don't do weird things like making the first move empty or it'll get stuck using Tackle.

i've only used this with the original Chinese version.
i don't use patches for the game, so if you're using some translation patch, i can't guarantee compatibility.
the editor displays in English, but you can edit the names in speciesIndex and moveIndex to translate to other languages.

when editing moves, the current number of Power Points (PP) in them won't be edited.
because of this, they can end up higher than the maximum PP for the new move.
but this shouldn't cause problems, and using the move enough or healing at the PokéCen will fix it anyways.

Kyogre, Groudon, and Rayquaza can't normally be obtained, but you can edit them in if you want.
i didn't add Missingno (looks like a "?") to the editor because it's not friendly (breaks the game).
<br><hr><br>
Credits:<br>
checksum logic is followed from Inkbox on YouTube.
they made the getRareCandy.py, i adapted it for some other items.
i also used their <a href="https://www.youtube.com/watch?v=WJmAl2DNvU8">video</a> for the completePokedex.py.
for the Pokédex and item scripts, you need to manually put edit in the input and output file names.
put the save file to edit in the same directory and edit the name into the py file.

i used the English names and move indexes from a spreadsheet by "Kingpepe".
English isn't my first language so if you don't know what the moves do, you can <a href="https://docs.google.com/spreadsheets/d/16a-fot8BFq7Q11ahwKa7js8pkC8aGfxMHlWW0AK9koY/edit?gid=1053279941#gid=1053279941">go look at it</a>.

it's not hard to expand this but i don't have the time, so feel free to take it and make it better.