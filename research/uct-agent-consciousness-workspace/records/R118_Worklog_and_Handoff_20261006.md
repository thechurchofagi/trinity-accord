# R118 工作记录与交接 — biological public-data boundary audit

日期：2026-10-06。

重要纠正：Neuron 2026 Figshare 12个MATLAB文件是5只recording rats的neural recording sessions，适合B1/B2；Figure3 projection/whole-region optogenetic behavior是另一套session registry + BControl trial data。GitHub里的optodata_FOFSTR.xlsx只是session registry，package_pbups_opto_DG.m会用ratname+sess_id从实验室behavioral-control数据源重建trial data。因此即使1.8GB Cells.zip成功下载，也不能自动说完成B3 trial-level复算。

已在connector runtime直接解析49KB xlsx：
raw 309 session rows；
按作者figure1_metaopto.m exclusion：probe!=0.6且去X025/X038/X011后222 sessions；
cntrl=0 inactivation 165，cntrl=1 control 57；
left139/right83；
rat counts：X00824,X00248,X0139,X02621,X03335,X04426,X0425,X04817,X05019,X03718。

作者trial timing code已独立核对：
optoval0 none；
1 whole trial2s；
2 pre-stim；
3 first half；
4 second half；
5 memory；
6 movement。
Figure3主分析比较1/3/4。

因此B1/B2可等1.8GB raw transfer后独立复算；B3当前只用peer-reviewed perturbation result + independently audited design/registry，不冒充trial replication。

下一步R119不再被数据下载卡住，先形式化T2 intervention-preserving support correspondence certificate；以后任何biology/AI数据都直接插入统一certificate。
