% List of words to ignore
ignore_word(and).
ignore_word(but).
ignore_word(in).
ignore_word(for).
ignore_word(the).
ignore_word(what).
ignore_word(how).
ignore_word(who).
ignore_word(very).
ignore_word(with).
ignore_word(of).
ignore_word(as).
ignore_word(a).
ignore_word(an).
ignore_word(there).
ignore_word(is).
ignore_word(our).
ignore_word(on).

% Rules for keyword matching in title and abstract
keyword_match(K, t) :- not ignore_word(T), metadata_title_word(T), keyword(K), T = K.
keyword_match(K, a) :- not ignore_word(A), metadata_abstract_word(A), keyword(K), A = K.

% Calculate total score
score(S) :- #count{K, I : keyword_match(K, I)} = S.


#show score/1.
