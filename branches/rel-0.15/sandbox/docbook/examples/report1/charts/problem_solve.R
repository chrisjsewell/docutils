# load("rates")
rates <- read.csv("../tables/all.csv")
path = 'problem_solve_2010_2011.png'
title = "Problem Solving,  2010, 2011"
x <- rates$week
y1 <- rates$hours.problem.solve.2010 
y2 <- rates$hours.problem.solve.2011
total.hours.2010 <- rates$hours.outbound.2010 + rates$hours.inbound.2010
total.hours.2011 <- rates$hours.outbound.2011 + rates$hours.inbound.2011
y1 <- y1/total.hours.2010
y2 <- y2/total.hours.2011
y1 <- y1 * 100
y2 <- y2 * 100
png(file=path,
width=5, height=3.5, units="in", res=res)
xlab.text="Week in Year"
xlab = xlab.text
ylab = "percentage to total"
if (make.title == T ) top.margin = 3
if (make.title != T ) title="" 
if (months.grid == T) bottom.margin = 6
if (months.grid == T) xlab = ''
margins=c(bottom.margin, 4, top.margin, 0.5) 
par(mar=margins) 
par(mar=margins) 
par('family'='serif')
y_range = range(y1,y2, na.rm=T)
plot(x, type='n', xlab=xlab, ylab=ylab, las=1, main=title, 
        ylim=c(y_range), axes=F, xlim=c(range(x)))
axis(1, col=ax_col)
axis(2, col=ax_col, las=1, at=axTicks(2))
box(col=box_col)
abline( h=axTicks(2), lty=1, lwd=lwd_grid, col=ax_col)

lines(x,y1,  col=line_colors[1], type="l", lwd=lwd, lty=line_types[1])
lines(x,y2,  col=line_colors[2], type="l", lwd=lwd, lty=line_types[2])
arrows(x0=30, x1=36, y0=5, y1=5, length=.1)
text(x=30, y=5, pos=2, "cutover")
source("make_x_axis.R")
legend("topleft", c("2010","2011"), cex=legend_font_size, 
 col=line_colors,  lty=line_types,  bty='y', bg="white", box.lwd=box.lwd)
dev.off()
