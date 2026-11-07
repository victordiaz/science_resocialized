clear


***********************************
import delimited "../Data/FishingExpInitialPars_all.txt", clear delimiter(tab) varnames(nonames)

rename (v1 v2 v13 v14 v15) ///
	(subject write_time age race gender)

replace subject = substr(subject,2,.)
destring subject, replace
	
foreach catvar in race gender{
	encode `catvar', ge(`catvar'2)
	order `catvar'2, after(`catvar')
	drop `catvar'
	rename `catvar'2 `catvar'
}
// Gender: 1 - Female; 2 - Male

foreach datevar in write_time {
	replace `datevar' = substr(`datevar',5,.)
	replace `datevar' = subinstr(`datevar'," CET "," ",.)
	gen `datevar'2 = clock(`datevar', "MDhmsY")
	order `datevar'2, after(`datevar')
	format `datevar'2 %tc
	drop `datevar'
	rename `datevar'2 `datevar'
}

// Due to issues with program:
bysort subject (write_time): gen dup = ([_n]!=[_N])
drop if dup==1

// Same subject, something went wrong with program and had to start over. We drop this:
drop if subject==550 | subject==551

gen id = ceil(1000000*runiform())
replace id=id+99999 if id<100000
qui duplicates r id
if r(N)!=r(unique_value){
	while r(N)!=r(unique_value){
		replace id = ceil(999999*runiform())
		replace id=id+99999 if id<100000
		qui duplicates r id
	}
}
order id, after(subject)

save "use/FishingExpInitialPars.dta", replace


***********************************
import delimited "../Data/fishingData_all.txt", clear delimiter(tab) varnames(nonames)

rename (v1 v2 v3 v4 v5 v6 v7 v8 v9 v10 v11 v12 v13) ///
	(subject start_time write_time practice how_many_fish num_trips release_rule weather visit casts bluefish cast_data response_time)

replace subject = substr(subject,2,.)
destring subject, replace

	
foreach catvar in practice release_rule weather{
	encode `catvar', ge(`catvar'2)
	order `catvar'2, after(`catvar')
	drop `catvar'
	rename `catvar'2 `catvar'
}
// Practice: 1 - Practice; 2 - Test (not practice)
// Release rule: 1 - Keep; 2 - Release
// Weather: 1 - Clear; 2 - Cloudy

foreach datevar in start_time  write_time{
	replace `datevar' = substr(`datevar',5,.)
	replace `datevar' = subinstr(`datevar'," CET "," ",.)
	gen `datevar'2 = clock(`datevar', "MDhmsY")
	order `datevar'2, after(`datevar')
	format `datevar'2 %tc
	drop `datevar'
	rename `datevar'2 `datevar'
}


merge m:1 subject using "use/FishingExpInitialPars.dta", keepusing(id)
drop _merge
order id, after(subject)
drop subject
save "use/fishingData.dta", replace


***********************************
import delimited "../Data/DopertData_all.txt", clear delimiter(tab) varnames(nonames)

rename (v1 v2 v3 v4 v5 v6 v7 v8 v9) ///
	(subject start_time write_time dopertType qOrder qID qText domain answer)

replace subject = substr(subject,2,.)
destring subject, replace

replace domain = "1" if domain=="E"
replace domain = "2" if domain=="I"
replace domain = "3" if domain=="G"
replace domain = "4" if domain=="H"
replace domain = "5" if domain=="R"
replace domain = "6" if domain=="S"

// Ethics, Investment, Gambling, Health/ safety, Recreational, and Social

destring domain, replace

label define domaintype 1 "ethics" 2 "investment" 3 "gambling" 4 "health/safety" 5 "recreational" 6 "social"
label values domain domaintype

foreach datevar in start_time  write_time{
	replace `datevar' = substr(`datevar',5,.)
	replace `datevar' = subinstr(`datevar'," CET "," ",.)
	gen `datevar'2 = clock(`datevar', "MDhmsY")
	order `datevar'2, after(`datevar')
	format `datevar'2 %tc
	drop `datevar'
	rename `datevar'2 `datevar'
}

merge m:1 subject using "use/FishingExpInitialPars.dta", keepusing(id)
drop _merge
order id, after(subject)
drop subject
save "use/DopertData.dta", replace


***********************************
import delimited "../Data/DrugData_all.txt", clear delimiter(tab) varnames(nonames)

rename (v1 v2 v3 v4 v5 v6 v7 v8 v9 v10) ///
	(subject start_time write_time qCumulative qID topicOrder qType qText answer answerExp)
	
replace subject = substr(subject,2,.)
destring subject, replace

label define type 0 "Used" 1 "Now" 2 "Most"
label values qType type

gen int topic = qID if qType==0
order topic, before(topicOrder)
replace topic=topic[_n-1] if topic==.
label define drug 0 "Cannabis" 3 "Alcohol" 6 "Cocaine" 9 "MDM (ecstasy)" 12 "Stimulants" 15 "Sedatives/Hypnotics" 18 "Opiates" 21 "Hallucinogens" 24 "PCP" 27 "Inhalants" 30 "Nicotine"
label values topic drug


foreach datevar in start_time write_time {
	replace `datevar' = substr(`datevar',5,.)
	replace `datevar' = subinstr(`datevar'," CET "," ",.)
	gen `datevar'2 = clock(`datevar', "MDhmsY")
	order `datevar'2, after(`datevar')
	format `datevar'2 %tc
	drop `datevar'
	rename `datevar'2 `datevar'
}

// From paper:
// "After each yes/no question, participants were also asked to report about how often they used the drug at the time
//  in their life when they used it the most frequently (i.e., never, one time, monthly or less, 2 to 4 times a month,
//  2 to 3 times a week, or 4 or more times a week). Weighting the categories that participants reported trying with
//  the frequency rank and summing created the measure identified as weighted polydrug."

bysort subject: egen polydrug = total(answer-1) if qType==2
bysort subject: egen testeddrugs = count(polydrug)

merge m:1 subject using "use/FishingExpInitialPars.dta", keepusing(id)
keep if _merge==3 | _merge==1
drop _merge
order id, after(subject)
drop subject
drop if id==.

save "use/DrugData.dta", replace

collapse (max) polydrug testeddrugs, by(id)
replace polydrug=0 if polydrug==.
save "use/polydrug.dta", replace

**********

use "use/FishingExpInitialPars.dta",clear
drop subject
save "use/FishingExpInitialPars.dta", replace



********** table6data
// "The adjusted ART score is the average number of casts taken on rounds when participants chose to stop fishing."

// "After each yes/no question, participants were also asked to report about how often they used the drug at the time
//  in their life when they used it the most frequently (i.e., never, one time, monthly or less, 2 to 4 times a month,
//  2 to 3 times a week, or 4 or more times a week). Weighting the categories that participants reported trying with
//  the frequency rank and summing created the measure identified as weighted polydrug."

use "use/fishingData.dta", clear
collapse casts if bluefish==0, by(id weather release_rule)
gen int condition = 10*release_rule+weather
drop weather release_rule

reshape wide casts, i(id) j(condition)
rename casts11 KS
rename casts12 KC
rename casts21 RS
rename casts22 RC

merge 1:1 id using "use/polydrug.dta"
replace polydrug=1 if polydrug==. & _merge==3

drop _merge
merge 1:1 id using "use/FishingExpInitialPars.dta", keepusing(gender age)
drop _merge

// Not all answered drug questionnaire and hence will not have been matched:
drop if id==.
save "use/table6data.dta", replace
