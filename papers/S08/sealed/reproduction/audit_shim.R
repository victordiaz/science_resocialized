# Loading shim for running RPP_mua6d.R unchanged except for data access:
# httr/RCurl are absent and the script sources getOSFfile from sachaepskamp.com
# (outside the allowed hosts), so getOSFfile is redefined to return the file
# already downloaded from the same OSF guid. Nothing else in the script is touched.
.local <- c("https://osf.io/dy3zn/" = "download/Data/McCrea.csv")
library <- function(pkg, ...) { p <- as.character(substitute(pkg)); if (p %in% c("httr","RCurl")) return(invisible(NULL)); base::library(p, character.only = TRUE, ...) }
getOSFfile <- function(url, ...) unname(.local[url])
source <- function(file, ...) { if (grepl("sachaepskamp", file)) return(invisible(NULL)); base::source(file, ...) }
base::source("download/Analysis_Audit/RPP_mua6d.R", echo = TRUE, max.deparse.length = 1e4)
