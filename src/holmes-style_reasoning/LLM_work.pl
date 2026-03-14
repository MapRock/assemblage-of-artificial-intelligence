% ------------------------------------------------------------
% A. Problem statement
% ------------------------------------------------------------

premise(open_question, 
        'Chickens (Gallus gallus domesticus) are not native to the Americas, so their presence requires introduction by some mechanism(s), potentially multiple over time').

% ------------------------------------------------------------
% B. Fact inventory
% ------------------------------------------------------------

fact(1, 'Chickens were domesticated from red junglefowl in Southeast Asia / East Asia around 9000 years ago or earlier').
fact(2, 'Chickens appear in Pacific archaeological sites starting approximately 3000 years ago (e.g., Reef/Santa Cruz, Vanuatu)').
fact(3, 'Chicken bones (50 specimens, minimum 5 individuals) were recovered from the El Arenal-1 site on the Arauco Peninsula, south central Chile').
fact(4, 'The El Arenal-1 site is located ~3-5 km inland on the southern side of the Arauco Peninsula').
fact(5, 'Radiocarbon dating on an El Arenal chicken bone yielded 622 ± 35 BP, calibrated to AD 1304–1424 (or AD 1321–1407 at intercepts), pre-Columbian era').
fact(6, 'Thermoluminescence dates on ceramics from El Arenal-1 place occupation between AD 700 and 1390').
fact(7, 'Ancient mtDNA from an El Arenal chicken bone matched sequences from prehistoric Pacific sites (e.g., identical to bones from Mele Havea in Tonga and Fatu-ma-Futi in American Samoa)').
fact(8, 'The matched ancient DNA haplotype was associated with Polynesian contexts in initial studies').
fact(9, 'Modern South American chickens show predominant mtDNA haplogroup E (e.g., ~84% in some studies), common in European, Indian, Middle Eastern, and some Chinese chickens').
fact(10, 'Other haplogroups in South American chickens include A, B, C, D at lower frequencies').
fact(11, 'Haplogroup D is common in modern Island Southeast Asia and Pacific islands but not observed or rare in continental South America').
fact(12, 'Sub-haplogroups like A1a(b) and E1a(b) in South America were previously observed mainly in Eastern Asia').
fact(13, 'Araucana chickens (from Mapuche region, Chile) exhibit unique traits: blue/green eggs, ear tufts, rumplessness (tailless); some traits (e.g., blue eggs, ear tufts) arose as mutations in South America').
fact(14, 'Ear tufts and rumplessness are homozygous lethal traits in Araucana, leading to partial lethality in breeding').
fact(15, 'Spanish accounts in the 1500s (e.g., Pizarro in Peru 1532) noted chickens integrated into Incan culture and ceremonies').
fact(16, 'European chickens were introduced to the Americas post-1492 by Spanish, Portuguese, etc., often via Atlantic routes').
fact(17, 'Some ancient Pacific chicken DNA shows haplogroup E, but later studies identified contamination issues with modern DNA in some analyses').
fact(18, 'Reanalyses (e.g., 2014) found no diagnostic Polynesian mtDNA haplotypes (e.g., certain D or others) in early South American samples').
fact(19, 'Modern Chilean chickens cluster with Indo-European/Asian haplotypes, not exclusively Polynesian').
fact(20, 'Chickens reached Easter Island pre-European contact via Polynesian dispersal').
fact(21, 'No pre-Columbian chicken evidence exists in the Americas outside debated South American sites like El Arenal').
fact(22, 'Multiple centers of chicken domestication/early dispersal occurred in South/Southeast Asia').

% ------------------------------------------------------------
% C. Factual/clue space
% ------------------------------------------------------------

entity('Chickens (Gallus gallus)').
entity('Polynesians').
entity('Europeans (Spanish/Portuguese)').
entity('Mapuche/Incan peoples').
entity('red junglefowl ancestor').

constraint('Chickens cannot fly long distances or cross oceans naturally; require human transport').
constraint('Oceanic crossing to South America possible via Pacific (Polynesian voyaging canoes) or Atlantic (European ships post-1492)').
constraint('mtDNA haplogroups show lineage inheritance; contamination risks in ancient DNA; lethal traits (e.g., Araucana) limit spread without human selection').
constraint('El Arenal dates ~AD 1300–1400 predate European arrival ~AD 1492–1530s; Polynesian Pacific expansion ~1000 BC onward, eastern Polynesia ~AD 1000+').

open_question('Extent of modern DNA contamination in early ancient chicken studies from Pacific/South America').

relation('Earliest confirmed chicken bones in Americas at El Arenal; no earlier sites').
relation('Predominant modern South American haplogroups align with European/Asian sources; lack of exclusive Polynesian markers in reanalyses').

% ------------------------------------------------------------
% D. Candidate hypotheses
% ------------------------------------------------------------

hypothesis(1, 'Chickens arrived via pre-Columbian Polynesian contact across the Pacific, introducing birds to Chile ~AD 1300s').
hypothesis(2, 'Chickens arrived exclusively post-Columbian via European (Spanish/Portuguese) introduction after 1492, with earlier dates contaminated or misinterpreted').
hypothesis(3, 'Multiple introductions: early pre-Columbian (Polynesian) plus later European overlay, with European lineages dominating modern populations').
hypothesis(4, 'Accidental or drift introduction via natural rafting or lost birds from early Asian/European ships, but human-mediated').
hypothesis(5, 'Independent domestication or survival from ancient natural dispersal, but contradicted by biology').

% ------------------------------------------------------------
% E. Deductions from each hypothesis
% ------------------------------------------------------------

deduction(1, timing, 'Introduction ~AD 1300–1400 via Pacific').
deduction(1, route, 'Polynesian voyaging from eastern Pacific islands (e.g., Easter Island vicinity) to Chile').
deduction(1, biological_form, 'Polynesian-stock birds (e.g., haplogroup E or Pacific variants)').
deduction(1, linguistic, 'Possible loanwords in Mapuche/Incan for chicken').
deduction(1, archaeological, 'Pre-Columbian bones like El Arenal').
deduction(1, dna, 'Polynesian haplotypes in ancient South American samples').
deduction(1, contamination, 'Sensitive to modern DNA overwrite').
deduction(1, contact_type, 'Likely one-time or limited contact').

deduction(2, timing, 'Post-1492, possibly 1500s').
deduction(2, route, 'Atlantic from Europe/Iberia').
deduction(2, biological_form, 'European/Indo-European haplogroups').
deduction(2, linguistic, 'Spanish/Portuguese-derived terms').
deduction(2, archaeological, 'No pre-1492 bones; El Arenal dates erroneous').
deduction(2, dna, 'European haplogroups dominant; no Pacific markers').
deduction(2, contamination, 'Vulnerable to old carbon or misdating').
deduction(2, contact_type, 'Repeated European introductions').

deduction(3, timing, 'Pre-Columbian (~1300s) plus post-1492').
deduction(3, route, 'Pacific then Atlantic').
deduction(3, biological_form, 'Mixed Polynesian + European').
deduction(3, linguistic, 'Mixed influences').
deduction(3, archaeological, 'Early bones + later spread').
deduction(3, dna, 'Early Pacific signals overwritten by European').
deduction(3, contamination, 'High sensitivity to later admixture').
deduction(3, contact_type, 'Repeated contacts').

deduction(4, timing, 'Variable, possibly early accidental').
deduction(4, route, 'Non-deliberate (e.g., rafting)').
deduction(4, biological_form, 'Whatever survived drift').
deduction(4, linguistic, 'None specific').
deduction(4, archaeological, 'Sparse early evidence').
deduction(4, dna, 'Random haplogroups').
deduction(4, contamination, 'Less predictable').
deduction(4, contact_type, 'Rare/one-time').

deduction(5, timing, 'Ancient pre-human').
deduction(5, route, 'Natural migration').
deduction(5, biological_form, 'Native-like').
deduction(5, linguistic, 'Indigenous terms').
deduction(5, archaeological, 'Deep-time bones').
deduction(5, dna, 'Distinct lineages').
deduction(5, contamination, 'N/A').
deduction(5, contact_type, 'Natural spread').

% ------------------------------------------------------------
% F. Elimination/pruning
% ------------------------------------------------------------

eliminated(5) :- 
    write('Conflicts with domestication facts (Southeast Asia origin) and no native Gallus in Americas').

weakened(4) :- 
    write('No evidence for non-human transport across vast ocean; human mediation required per constraints').

weakened(2) :- 
    write('Conflicts with El Arenal radiocarbon dates (~AD 1300s) and archaeological context pre-1492').

weakened(1) :- 
    write('Conflicts with reanalyses showing no exclusive Polynesian mtDNA in South America; contamination issues in initial studies; modern haplogroups align more with European/Asian').

survives(3) :- 
    write('Compatible with early El Arenal evidence (possible limited Polynesian input) plus dominant post-Columbian European overlay; explains mixed signals and modern predominance of haplogroup E').

% ------------------------------------------------------------
% G. Best surviving explanation
% ------------------------------------------------------------

best_explanation('Multiple introductions, with a possible limited pre-Columbian contact (likely Polynesian) introducing chickens by ~AD 1300–1400 to Chile (supported by El Arenal dates and initial DNA matches), followed by dominant post-Columbian European introductions after 1492 that overwhelmed earlier lineages genetically and numerically').

% ------------------------------------------------------------
% H. Residual uncertainties
% ------------------------------------------------------------

residual_uncertainty('Authenticity of early DNA matches vs. contamination').
residual_uncertainty('Whether El Arenal represents sustained population or isolated event').
residual_uncertainty('Full extent of pre-Columbian contact (genetic trace faint due to later admixture)').

% ------------------------------------------------------------
% I. Comparison with prevailing theory
% ------------------------------------------------------------

prevailing_theory('Chickens arrived primarily with Europeans post-1492, with pre-Columbian claims (e.g., Polynesian) largely rejected due to contamination in ancient DNA and lack of diagnostic Pacific markers in South America').

comparison_note('The above follows the strict elimination process, yielding a more tentative hybrid view, while acknowledging the mainstream leans heavily toward European introduction as the main/original mechanism').

% ------------------------------------------------------------
% Example query to explore
% ?- survives(H).
% ?- eliminated(Why).
% ?- best_explanation(E).
% ------------------------------------------------------------
