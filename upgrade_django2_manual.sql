/* Fixed name of formatbannedcard table. */
ALTER TABLE cards_formatbannedcard RENAME formatbannedcard;

/* Fixed name of formatexpansionset table. */
ALTER TABLE cards_formatexpansionset RENAME formatexpansionset;

/* Remove all previous migrations */
DELETE FROM django_migrations WHERE app IN ('mtgdbapp', 'cards','decks','rules','content');

INSERT INTO django_migrations (app, name, applied) VALUES ('cards','0001_initial', NOW());
INSERT INTO django_migrations (app, name, applied) VALUES ('decks','0001_initial', NOW());
INSERT INTO django_migrations (app, name, applied) VALUES ('content','0001_initial', NOW());
