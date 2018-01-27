;; Parser test input.

[
 ;; First and last names.
 "Fred" "Flintstone"

 ;; AKA.
 ("Freddie")

 ;; Company.
 "Slate Rock & Gravel"

 ;; Mapping of tag names to phone numbers.
 (["Home" "555-1234"] ["Work" "555-6789"])

 ;; Mapping of tag names to addresses.
 (["Home"
   ("Cave 2a" "345 Cavestone Road") "Bedrock" "Hanna Barbera" "12345" "USA"])

 ;; List of email addresses.
 ("fred@bedrock.org" "fred.flintstone@gravel.com")

 ;; Alist of fields.
 ((catchphrase . "\"Yabba dabba doo!\"")
  (kids . "Pebbles, Bam-Bam")
  (spouse . "Wilma"))

 ;; Unused cache field.
 nil
]
