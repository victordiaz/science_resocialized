
********************************************************************************
********************************************************************************
***
***
***		RPP Replication Study 
***
***		Alvarez, G.A., & Oliva, A. (2008). The Representation of Simple
***		Ensemble Visual Features Outside the Focus of Attention. Psychological
***		Science 19(4),392-398. doi: 10.1111/j.1467-9280.2008.02098.x 
***
********************************************************************************
***
***
***		Authors: 
***			René Schlegelmilch, PhD University of Erfurt, Germany
***			Research Fellow Minerva Group at the 
***			Max-Planck-Institute for Research on Collective Goods, Bonn, Germany
***			Mail: rene.schlegelmilch@uni-erfurt.de
***			&
***			Don van den Bergh
***			Mail: donvdbergh@hotmail.com
***
***
***
********************************************************************************
********************************************************************************

*Directory of Matlab Output Data
cd "F:\Projects\Replikation\Experiment\Participants_Data"
clear
set more off
*convert txt files to stata format
*for 17 Participants:
forval i=1(1)17 {
import delimited ".\Alvarez_`i'.txt", delimiters(" ")
gen subject=`i'
save ".\Alvarez_Participant`i'.dta"
clear
}
*::
*Merge to one file:
clear
use ".\Alvarez_Participant1.dta"
forval i=2(1)17 {
append using ".\Alvarez_Participant`i'.dta"
}
*::
*** rename Value Labels:
* Original Output Data Description from matlab, begins with v1... column wise
qui{
/*
data(:, 1) contains trialnumber
data(:, 2) contains condition (1 = distractor missing, 2 = target missing, 3=distractors missing, 4=targets missing)
data(:, 3) checks a time duration (flashing dots)
data(:, 4) checks a time duration (moving dots)
data(:, 5) contains amount of times dots cross the diagonal
data(:, 6) contains userinput
data(:, 7) contains the x coordinate of the missing dot/ centroid (centroid needs to be recalculated appropriately)
data(:, 8) contains the y coordinate of the missing dot/ centroid (centroid needs to be recalculated appropriately)
data(:, 9) contains the userinput mousex
data(:, 10) contains the userinput mousey
data(:, 11) contains sector in which target will be drawn. 1 is the upper half, 2 is the right half, 3 is the bottom half and 4 is the left half of the screen.
data(:, 12) contains the x coordinate of the missing dot 1 in case of 4 missing dots
data(:, 13) contains the y coordinate of the missing dot 1 in case of 4 missing dots
data(:, 14) contains the x coordinate of the missing dot 2 in case of 4 missing dots
data(:, 15) contains the y coordinate of the missing dot 2 in case of 4 missing dots
data(:, 16) contains the x coordinate of the missing dot 3 in case of 4 missing dots
data(:, 17) contains the y coordinate of the missing dot 3 in case of 4 missing dots
data(:, 18) contains the x coordinate of the missing dot 4 in case of 4 missing dots
data(:, 19) contains the y coordinate of the missing dot 4 in case of 4 missing dots
*/
rename v1 trial
rename v2 condition
label define condition 1 "One Distractor Missing" 2 "One Target Missing" 3 "All Distractors Missing" 4 "All Targets Missing"
gen tar_vs_dis=1
replace tar_vs_dis=11 if condition==1 | condition ==3
gen one_vs_four=1
replace one_vs_four=4 if condition==3 | condition ==4
drop v3
rename v4 trialduration
rename v5 crosscount
rename v6 Pcrosscount
rename v7 missing_x // in case of condition 3 and 4 this variable contains the centroid x localization
rename v8 missing_y // in case of condition 3 and 4 this variable contains the centroid y localization
rename v9 mouse_x
rename v10 mouse_y
drop v11
rename v12 x1
rename v13 y1
rename v14 x2
rename v15 y2
rename v16 x3
rename v17 y3
rename v18 x4
rename v19 y4
gen ExGuess = "experimental"
replace ExGuess = "guessing" if trialduration==0
replace tar_vs_dis=. if ExGuess=="guessing"
order ExGuess, first
order tar, first
order one, first
order subject, first
replace missing_x=. if condition==3 | condition==4 // in the matlab code in these conditions simple x and y means are calculated, but not the centroid
replace missing_y=. if condition==3 | condition==4
save ".\Alvarez_Data.dta", replace
*savecopy
save ".\centroids.dta", replace
}
*::
***
*Calculate Centroid Positions:
qui {
* we have to separate them into four triangles

*but for this purpose the x1...x4 and y1...y4 coordinates need to be rearranged
*to get the right order of the triangles... (opposite ones)
use ".\centroids.dta", clear

*it is necessary to calculate the centroid with edgepoints of the quadrilateral that go either strictly clockwise
*or counterclockwise *the following code makes sure that the edges are correctly identified
* the method to achieve that is:
* find the point to the very left
* calculate all angles to the other points
drop if x1==0
reshape long x y, i(subject ExGuess trial) j(original)
egen rankx = rank(x), by(subject ExGuess trial)
drop original
reshape wide x y, i(subject ExGuess trial) j(rankx)
*x1y1 now is the point at the very left
*to get the angle tan alpha is calculated
*therefore we need a 90° triangle
*so x1y1 is set to zero relative to the other points, then tang alpha = (x2-x1)/(y2-y1)
gen tanA1=-50
gen tanA2 =(y2-y1)/(x2-x1)
gen tanA3 =(y3-y1)/(x3-x1)
gen tanA4 =(y4-y1)/(x4-x1)
*so we reorder the set again according to tan alpha which now indicates a point order that fullfills the 
*same coordinate structure for every quadrilateral, we will later need this to know with which triangle we are calculating
reshape long tanA y x, i(subject ExGuess trial) j(original)
replace tanA=0 if tanA==. // because there are cases (always the same) where the two points lie on a parallel to the x-axis and there is an angle of zero
egen rankx = rank(tanA), by(subject ExGuess trial)
drop original
reshape wide tanA y x, i(subject ExGuess trial) j(rankx)

*for centroids of the quadrilaterals we first need the centroid of each triangle in it
* to calculate opposite triangles
* therfore I take the step over the order of x and y coordinates of the four missing points

gen xs_123 = (x1+x2+x3)/3
gen ys_123 = (y1+y2+y3)/3

*gen xs_234 = (x2+x3+x4)/3
*gen ys_234 = (y2+y3+y4)/3

gen xs_341 = (x3+x4+x1)/3
gen ys_341 = (y3+y4+y1)/3

*gen xs_412 = (x4+x4+x1)/3
*gen ys_412 = (y4+y4+y1)/3

*123 and 341 are oppisite triangles
*as 234 and 412 are : we only need two of them and there space, so taking the one opposite pair or the other will make no difference

*now the space of each triangle is needed - trapezoid method is used
*that is in general space=0.5(x1*(y2-y3)+x2(y3-y1)+x3*(y1-y2))
gen space123 = 0.5*(x1*(y2-y3)+x2*(y3-y1)+x3*(y1-y2))
*gen space234 = 0.5*(x2*(y3-y4)+x3*(y4-y2)+x4*(y2-y3))
gen space341 = 0.5*(x3*(y4-y1)+x4*(y1-y3)+x1*(y3-y4))
*gen space412 = 0.5*(x4*(y1-y2)+x1*(y2-y4)+x2*(y4-y1))

*and finally the coordinates of the centroid
*where the triangle centroid coordinates are weightes by the triangle mass/space
gen cX = (xs_123*space123+xs_341*space341)/(space123+space341)
gen cY = (ys_123*space123+ys_341*space341)/(space123+space341)

*We have the centroid now cX cY ... what a mess...
keep subject trial ExGuess cY cX
save ".\centroids.dta", replace

*merge with main file
use ".\Alvarez_Data.dta", clear
merge m:m subject ExGuess trial using ".\centroids.dta"

replace missing_x = cX if missing_x==.
replace missing_y = cY if missing_y==.
drop cX cY _merge
save ".\Alvarez_Data.dta", replace
}
*::
***
*Calculate distance (in degrees) between mouseclick and missing dots:
qui {
use ".\Alvarez_Data.dta", clear 
*first: conversion of coordinates in pixels to coordinates in cm
*for screen resolution 1600x900 and screen dimensions of 34,5 cm x 19,5 cm
gen miss_x_cm = missing_x/(1600/34.5)
gen mouse_x_cm = mouse_x/(1600/34.5)
gen miss_y_cm = missing_y/(900/19.5)
gen mouse_y_cm = mouse_y/(900/19.5)
*distance d= sqrt((x1-x2)^2+(y1+y2)^2) in cm
gen cm_d = sqrt((miss_x_cm-mouse_x_cm)^2+(miss_y_cm-mouse_y_cm)^2)
*convert to visual angle in degrees; assuming vision is centered on the mid of the distance cm_d
*the distance from the screen was 43 cm (chin rest was used)
gen g=(cm_d/2)/43
gen at = 2*atan(g)
gen angle= at*(180/_pi)
drop miss_* mouse_x_ mouse_y_ cm g at
save ".\Alvarez_Data.dta", replace
}
*::
//******************************************************************************
////////////////////////////////////////////////////////////////////////////////
// final stage of the document, starting analyses use ".\Alvarez_Data.dta" /////
////////////////////////////////////////////////////////////////////////////////
*Calculate Counting Accuracy:
qui {
use ".\Alvarez_Data.dta", clear
set more off
preserve
gen acc=sqrt((cross-Pcross)^2)
drop if Ex=="guessing"
collapse acc, by (subject)
collapse acc (sd) sd_acc=acc (count)n=acc 
gen LL95_acc = acc - invttail(n-1, 0.025)*(sd_acc/sqrt(n-1))
gen UL95_acc = acc + invttail(n-1, 0.025)*(sd_acc/sqrt(n-1))
n list acc sd_acc LL95_acc UL95_acc n
restore
}
*::
*RM ANOVA for checking if counting errors vary in with localization test:
*Note: Although the use of RM ANOVA for this design seems false to me according
*to the design, I adapted this way of testing according to the reported results in the
*original article, where two RM ANOVA are reported with residual degrees of freedom of 7
*which (with 8 participants) indicate two separate RM ANOVA in which one of the 
*within factors was neglected 
qui {
use ".\Alvarez_Data.dta", clear
set more off
preserve
gen acc=sqrt((cross-Pcross)^2)
drop if Ex=="guessing"
collapse acc, by (subject tar)
n di "Target vs. Distractor RM ANOVA"
n anova acc tar subject, repeated(tar) bse(subject)
n effectsize tar_vs_dis
restore 

preserve
gen acc=sqrt((cross-Pcross)^2)
drop if Ex=="guessing"
collapse acc, by (subject one_)
n di "Target vs. Distractor RM ANOVA"
n anova acc one_ subject, repeated(one_) bse(subject)
n effectsize one_vs_four
restore
}
*::
***
*Localization Error in Degrees for the Guessing Phase (Empirical Chance Level)
qui {
use ".\Alvarez_Data.dta", clear
set more off
preserve
drop if ExGuess=="experimental"
collapse angle, by (subject one_)
collapse angle (sd) sd_angle=angle (count)n=angle , by( one_)
gen LL95_angle = angle - invttail(n-1, 0.025)*(sd_angle/sqrt(n-1))
gen UL95_angle = angle + invttail(n-1, 0.025)*(sd_angle/sqrt(n-1))
gen SEM =sd_angle/sqrt(n-1)
n list  one_ angle sd_an SEM LL95_an UL95_an n
restore
}
*::
***
*Localization Error in Degrees for the Experimental Phase
* T-Test 1 for INDIVIDUAL Test: Target vs. Distractor
qui {
use ".\Alvarez_Data.dta", clear
set more off
preserve
drop if one_vs_four==4
collapse angle, by (subject tar)
rename angle angle_target
gen angle_dis = angle_target if tar==11
egen angle_distract = max(angle_dis), by(subject)
drop angle_dis
keep if tar==1
n ttest angle_target == angle_distract
*Cohens d was calculated by hand using d=t/(sqrt(n))
restore
*DESCRIPTIVES
preserve
drop if one_vs_four==4
collapse angle, by (subject tar)
collapse angle (sd) sd_angle=angle (count)n=angle , by( tar)
gen LL95_angle = angle - invttail(n-1, 0.025)*(sd_angle/sqrt(n-1))
gen UL95_angle = angle + invttail(n-1, 0.025)*(sd_angle/sqrt(n-1))
gen SEM =sd_angle/sqrt(n-1)
n di " "
n di " "
n di "Descriptives Target vs. Distractor Experimental - vs. One Missing Guess (.)"
n di "The difference to the t-test descriptives is due to less degrees of freedom (n-1), which were used for the following table"
n list  tar angle sd_an SEM LL95_an UL95_an n
restore
n di " "
n di "___________________________"
n di " "
n di "Was localization error below empirical chance?"
n di " --- Individual Task ---"
n di " - - - Targets - - - "
preserve
drop if one_vs_four==4
drop if tar==11
collapse angle, by (subject ExGuess)
rename angle angle_exp
gen angle_g = angle_exp if ExGuess=="guessing"
egen angle_guess = max(angle_g), by(subject)
drop angle_g
keep if ExGuess=="experimental"
n ttest angle_exp == angle_guess
*Cohens d was calculated by hand using d=t/(sqrt(n))
restore
n di "Was localization error below empirical chance?"
n di " --- Individual Task ---"
n di " - - - Distractors - - - "
preserve
drop if one_vs_four==4
drop if tar==1
collapse angle, by (subject ExGuess)
rename angle angle_exp
gen angle_g = angle_exp if ExGuess=="guessing"
egen angle_guess = max(angle_g), by(subject)
drop angle_g
keep if ExGuess=="experimental"
n ttest angle_exp == angle_guess
*Cohens d was calculated by hand using d=t/(sqrt(n))
restore


}
*::
***
* T-Test 1 for CENTROID Test: Target vs. Distractor
qui {
use ".\Alvarez_Data.dta", clear
set more off
preserve
drop if one_vs_four==1
collapse angle, by (subject tar)
rename angle angle_target
gen angle_dis = angle_target if tar==11
egen angle_distract = max(angle_dis), by(subject)
drop angle_dis
keep if tar==1
n ttest angle_target == angle_distract
*Cohens d was calculated by hand using d=t/(sqrt(n))
restore
*DESCRIPTIVES
preserve
drop if one_vs_four==1
collapse angle, by (subject tar)
collapse angle (sd) sd_angle=angle (count)n=angle , by( tar)
gen LL95_angle = angle - invttail(n-1, 0.025)*(sd_angle/sqrt(n-1))
gen UL95_angle = angle + invttail(n-1, 0.025)*(sd_angle/sqrt(n-1))
gen SEM =sd_angle/sqrt(n-1)
n di " "
n di " "
n di "Descriptives Target vs. Distractor Experimental - vs. One Missing Guess (.)"
n di "The difference to the t-test descriptives is due to less degrees of freedom (n-1), which were used for the following table"
n list  tar angle sd_an SEM LL95_an UL95_an n
restore
n di " "
n di "___________________________"
n di " "
n di "Was localization error below empirical chance?"
n di " --- Centroid Task ---"
n di " - - - Targets - - - "
preserve
drop if one_vs_four==1
drop if tar==11
collapse angle, by (subject ExGuess)
rename angle angle_exp
gen angle_g = angle_exp if ExGuess=="guessing"
egen angle_guess = max(angle_g), by(subject)
drop angle_g
keep if ExGuess=="experimental"
n ttest angle_exp == angle_guess
*Cohens d was calculated by hand using d=t/(sqrt(n))
restore
n di "Was localization error below empirical chance?"
n di " --- Centroid Task ---"
n di " - - - Distractors - - - "
preserve
drop if one_vs_four==1
drop if tar==1
collapse angle, by (subject ExGuess)
rename angle angle_exp
gen angle_g = angle_exp if ExGuess=="guessing"
egen angle_guess = max(angle_g), by(subject)
drop angle_g
keep if ExGuess=="experimental"
n ttest angle_exp == angle_guess
*Cohens d was calculated by hand using d=t/(sqrt(n))
restore


}
*::
