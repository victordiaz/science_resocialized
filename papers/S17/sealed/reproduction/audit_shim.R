# Loading shim for running RPP_sd7kg.R unchanged except for data access:
# httr/RCurl are absent and the script sources getOSFfile from sachaepskamp.com
# (outside the allowed hosts), so getOSFfile is redefined to return the file
# already downloaded from the same OSF guid (nd7we). Nothing else is touched.
.local <- c("https://osf.io/nd7we/" = "download/Data/LoBue & DeLoache Replication Final File Ready for Analysis.sav")
library <- function(pkg, ...) { p <- as.character(substitute(pkg)); if (p %in% c("httr","RCurl")) return(invisible(NULL)); base::library(p, character.only = TRUE, ...) }
getOSFfile <- function(url, ...) unname(.local[url])
source <- function(file, ...) { if (grepl("sachaepskamp", file)) return(invisible(NULL)); base::source(file, ...) }
base::source("download/Analysis Audit/RPP_sd7kg.R", echo = TRUE, max.deparse.length = 1e4)
