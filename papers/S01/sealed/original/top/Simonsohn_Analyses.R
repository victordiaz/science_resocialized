#Experiment 1

###Schnall et al.
#Create tnonct function, like SAS 
tnonct <- function(delta, pr, x, df) pt(x, df = df, ncp = delta) - pr 
#Get the ncp low 
out <- uniroot(tnonct, c(-10, 10), pr =.975, x = 1.905
               , df = 38) 
ncp_low=out$root 
ncp_low 

#Get the ncp high 
out <- uniroot(tnonct, c(-10, 10), pr =.025, x = 1.905
               , df = 38)

ncp_high=out$root 
ncp_high 

#Go from ncp to d 
dhigh=ncp_high/sqrt(20/2) 
dlow=ncp_low/sqrt(20/2) 

#print result 
dhigh 
dlow

############################################################################

###Besman et al.

#Create tnonct function, like SAS 
tnonct <- function(delta, pr, x, df) pt(x, df = df, ncp = delta) - pr 
#Get the ncp low 
out <- uniroot(tnonct, c(-10, 10), pr =.975, x = 1.8
, df = 58) 
ncp_low=out$root 
ncp_low 

#Get the ncp high 
out <- uniroot(tnonct, c(-10, 10), pr =.025, x = 1.8
, df = 58)

ncp_high=out$root 
ncp_high 

#Go from ncp to d 
dhigh=ncp_high/sqrt(30/2) 
dlow=ncp_low/sqrt(30/2) 

#print result 
dhigh 
dlow

############################################################################

###Johnson et al.

#Create tnonct function, like SAS 
tnonct <- function(delta, pr, x, df) pt(x, df = df, ncp = delta) - pr 
#Get the ncp low 
out <- uniroot(tnonct, c(-10, 10), pr =.975, x = .066
               , df = 206) 
ncp_low=out$root 
ncp_low 

#Get the ncp high 
out <- uniroot(tnonct, c(-10, 10), pr =.025, x = .066
               , df = 206)

ncp_high=out$root 
ncp_high 

#Go from ncp to d 
dhigh=ncp_high/sqrt(104/2) 
dlow=ncp_low/sqrt(104/2) 

#print result 
dhigh 
dlow

############################################################################
#Experiment 2

###Schnall et al.
#Create tnonct function, like SAS 
tnonct <- function(delta, pr, x, df) pt(x, df = df, ncp = delta) - pr 
#Get the ncp low 
out <- uniroot(tnonct, c(-10, 10), pr =.975, x = 2.794
               , df = 41) 
ncp_low=out$root 
ncp_low 

#Get the ncp high 
out <- uniroot(tnonct, c(-10, 10), pr =.025, x = 2.794
               , df = 41)

ncp_high=out$root 
ncp_high 

#Go from ncp to d 
dhigh=ncp_high/sqrt(21.5/2) 
dlow=ncp_low/sqrt(21.5/2) 

#print result 
dhigh 
dlow


############################################################################

###Johnson et al.

#Create tnonct function, like SAS 
tnonct <- function(delta, pr, x, df) pt(x, df = df, ncp = delta) - pr 
#Get the ncp low 
out <- uniroot(tnonct, c(-10, 10), pr =.975, x = .032
               , df = 124) 
ncp_low=out$root 
ncp_low 

#Get the ncp high 
out <- uniroot(tnonct, c(-10, 10), pr =.025, x = .032
               , df = 124)

ncp_high=out$root 
ncp_high 

#Go from ncp to d 
dhigh=ncp_high/sqrt(63/2) 
dlow=ncp_low/sqrt(63/2) 

#print result 
dhigh 
dlow