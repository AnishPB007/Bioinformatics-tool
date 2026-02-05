args <- commandArgs(trailingOnly = TRUE)
sequence <- toupper(gsub("\\s+", "", args[1]))
sequence <- gsub("[^ACGTUN]", "", sequence)
if (nchar(sequence) == 0) {
  cat(0)
  quit(status = 0)
}

bases <- strsplit(sequence, "")[[1]]
count_gc <- sum(bases %in% c("G", "C"))
percentage <- round((count_gc / length(bases)) * 100, 2)
cat(percentage)
