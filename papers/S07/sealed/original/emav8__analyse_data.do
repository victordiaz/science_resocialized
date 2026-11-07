clear

**** Analysis ****
use "table6data.dta", clear

* Gender distribution (for participants with valid polydrug data)
tab gender if polydrug!=.

* Age distribution (for participants with valid polydrug data)
sum age if polydrug!=.

* Summary of number of tested drugs (for participants with valid polydrug data)
sum testeddrugs if polydrug!=., d

* Summary of the polydrug measure (for participants with valid polydrug data)
sum polydrug, d

* Summary of the Adjusted ART score (for participants with valid polydrug data)
sum KS KC RS RC if polydrug!=.

* Correlations between the polydrug measure and Ajusted ART scores in the different conditions (for participants with valid polydrug data)
pwcorr polydrug KS KC RS RC if polydrug!=.
