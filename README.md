# Hypotactic for NLP

An effort to make David Chamberlain's metrically marked-up corpus of Ancient Greek verse as easily accesible to NLP researchers as possible. David wrote "please take the data and see what you can do with it", and thus we do!

## Syllabification

My main contribution is to have adjusted the syllabification to comply with standard linguistic accounts of Ancient Greek. Scripts to perform this adjustment can be found in the `adjust_syllabification` folder. A single file containing 60660 adjusted lines can be found at [here](adjust_syllabification/hypotactic_all_shuffled_cleaned.txt).

**Caveat emptor:** The syllabification has run with heterosyllabic mute-with-liquid-or-nasal combinations across the board. This works for tragic drama, but epic use is more varied, and many lines thus have bugs, which should be kept in mind.
 
## Licence

The corpus is published on the [Hypotactic website](https://hypotactic.com/latin/index.html) under the [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) licence, which is interpreted by David Chamberlain (University of Oregon) himself in the following way:

> All the data on this site is/are licensed as CC-BY 4.0. That means that you can use it as you wish, but if you make significant or extensive use of it in published work you should reference me (David Chamberlain) and this site (hypotactic.com) as the source of the information (this constitutes my interpretation of the licence's "reasonable manner" language). By "data" I mean the tagging of individual syllables of verse with metrical attributes such as quantity, elision, hiatus, synizesis etc., and the identification of those syllables as independent metrical units.* To be clear, I do not intend to place any restrictions that go beyond standard academic attribution conventions; rather, I would like to encourage others to use the data as they will. The licence is intended to reassure you that that's OK.