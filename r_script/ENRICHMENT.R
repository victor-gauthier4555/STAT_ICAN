#test
#Working_directory =  "C:/Users/Rose Tchala Sare/Documents/application/static/data"
#setwd('Working_directory')
#df = read.csv("Timepoints_SIGNIFICANTS.csv", sep = ";")

#Commandes
args <- commandArgs(trailingOnly = TRUE)
file = args[1] ; filename1 = args[2] ;  filename2 = args[3] 

df = read.csv(file, sep = ";")
df1 = df[order(df[,5]),]

#BAR CHART
#setting the color palette
color_palette <-  colorRampPalette(c("yellow2", "orange","red"))(nrow(df))
#creating the barplot
png(file = filename1)
par(mar = c(5, 11, 4, 2))  # Increase left margin
barplot(df1[,5], horiz = T,
        xlab = "Enrichment Ratio", ylab = "",
        main = "Enriched Pathways", names.arg = df1[,1],
        las  = 1, cex.names = 0.5)
grid(lty=2, col='lightgray')
barplot(df1[,5], horiz = T, xlab = " ", ylab = "", main = "Enriched Pathways", names.arg = df1[,1], las  = 1, cex.names = 0.5,
        col = color_palette,
        add = T
)

dev.off()


#DOTPLOT
#par(mfrow = c(1, 2))
original_par <- par()
#windows(width = 12, height = 8)
dev.new(500,500)
png(file = filename2,  width = 1200, height = 800, res = 100)
layout_matrix <- matrix(c(1, 2), nrow = 1, ncol = 2)
widths <- c(2, 1)  # The first plot will be twice as wide as the second plot
layout(layout_matrix, widths = widths)

df1 = df[order(df$P.Value, decreasing = T),]
par(mar = c(5, 11, 4, 2))  # Increase left margin
plot(x = -log10(df1$P.Value), y = seq(from = 1, to = nrow(df)), 
     axes = F,
     yaxt = "n",
     xaxt = "n",
     xlab = "",
     ylab = "")
grid(lty=2, col='lightgray')
par(new = TRUE)
plot(x = -log10(df1$P.Value), y = seq(from = 1, to = nrow(df)), main = "Enriched Metabolites", xlab = "-log10 (P-Value)", ylab = "",
     col = heat.colors(nrow(df1), rev = T),
     pch = 16,
     yaxt = "n",
)
axis(2, at = seq(from = 1, to = nrow(df)), labels = df1$Pathway.name, las = 2, cex.axis = 0.5)

#legend color scale
colfunc <- colorRampPalette(heat.colors(nrow(df1), rev = T))
legend_image <- as.raster(matrix(colfunc(20), ncol=1))
plot(c(0,2),c(0,1),type = 'n', axes = F,xlab = '', ylab = '', main = 'P-Value')
text(x=1.5, y = seq(0,1,l=5), labels = seq(0,1,l=5))
rasterImage(legend_image, 0, 0, 1,1)




dev.off()
