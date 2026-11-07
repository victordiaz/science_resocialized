# Runs RPP_79dey.R unchanged except its loading lines: library(httr), library(RCurl) and source(getOSFfile.R) are dropped (not installed / external URL),
# and getOSFfile() is defined to return the downloaded file for osf.io/3xv8u.
.map <- c("https://osf.io/3xv8u/" = normalizePath("download/reconciling.for.repro.txt"))
getOSFfile <- function(url) .map[[url]]
lines <- readLines("download/RPP_79dey.R", warn = FALSE)
drop <- grepl("^library\\(\"(httr|RCurl)\"\\)", lines) | grepl("getOSFfile.R", lines, fixed = TRUE)
cat("dropped lines:\n"); cat(lines[drop], sep = "\n")
source(exprs = parse(text = lines[!drop]), echo = TRUE, max.deparse.length = 300)
