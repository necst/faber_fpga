fileFolder = CT_path;
%disp(fileFolder)
fileFolder1 = PET_path;
%disp(fileFolder1)

files=dir(fullfile(fileFolder,'*.dcm'));
files1=dir(fullfile(fileFolder1,'*.dcm'));

names={files.name};
[~, reindex] = sort( str2double(regexp({files.name}, '\d+', 'match', 'once' )));
names = names(reindex) ;
names1={files1.name};
[~, reindex1] = sort( str2double(regexp({files1.name}, '\d+', 'match', 'once' )));
names1 = names1(reindex1) ;

for i=length(names):-1:1
    fname=fullfile(fileFolder,names{i});
    REF(:,:,i)=uint16(dicomread(fname));        
end
 
for i=length(names1):-1:1
    fname1=fullfile(fileFolder1,names1{i});
    FLT(:,:,i)=uint16(dicomread(fname1));        
end

infoCT = dicominfo(fullfile(fileFolder,names{1}));
infoPET=dicominfo(fullfile(fileFolder1,names1{1}));

%CT%
Str_REF=struct;
Str_REF.nSeries=1;
Str_REF.seriesDate = infoCT.SeriesDate;
Str_REF.seriesTime = infoCT.SeriesTime;
Str_REF.modality = infoCT.Modality;
Str_REF.gantryModel =infoCT.ManufacturerModelName;
Str_REF.volumes = REF;
Str_REF.IOP = infoCT.ImageOrientationPatient;
for i=length(names1):-1:1
    t=dicominfo(fullfile(fileFolder,names{i}));
    Str_REF.IPP(:,i)=t.ImagePositionPatient;
end
Str_REF.imSz1 = size(Str_REF.volumes,1);
Str_REF.imSz2 = size(Str_REF.volumes,2);
Str_REF.imSz3 = size(Str_REF.volumes,3);


[temp2,temp1] = meshgrid(0:Str_REF.imSz2-1,0:Str_REF.imSz1-1); 
Str_REF.locX = zeros(Str_REF.imSz1,Str_REF.imSz2,Str_REF.imSz3);
Str_REF.locY = zeros(Str_REF.imSz1,Str_REF.imSz2,Str_REF.imSz3);
Str_REF.locZ = zeros(Str_REF.imSz1,Str_REF.imSz2,Str_REF.imSz3);

temp = repmat(Str_REF.IPP(:,1),1,Str_REF.imSz1*Str_REF.imSz2)+[Str_REF.IOP(1) Str_REF.IOP(2) Str_REF.IOP(3)]'*temp1(:)'*infoCT.PixelSpacing(2)+[Str_REF.IOP(4) Str_REF.IOP(5) Str_REF.IOP(6)]'*temp2(:)'*infoCT.PixelSpacing(1);
Str_REF.locX(:,:,1) = reshape(temp(1,:),Str_REF.imSz1,Str_REF.imSz2);
Str_REF.locY(:,:,1) = reshape(temp(2,:),Str_REF.imSz1,Str_REF.imSz2);
Str_REF.locZ(:,:,1) = reshape(temp(3,:),Str_REF.imSz1,Str_REF.imSz2);


temp = repmat(Str_REF.IPP(:,end),1,Str_REF.imSz1*Str_REF.imSz2)+[Str_REF.IOP(1) Str_REF.IOP(2) Str_REF.IOP(3)]'*temp1(:)'*infoCT.PixelSpacing(2)+[Str_REF.IOP(4) Str_REF.IOP(5) Str_REF.IOP(6)]'*temp2(:)'*infoCT.PixelSpacing(1);
Str_REF.locX(:,:,end) = reshape(temp(1,:),Str_REF.imSz1,Str_REF.imSz2);
Str_REF.locY(:,:,end) = reshape(temp(2,:),Str_REF.imSz1,Str_REF.imSz2);
Str_REF.locZ(:,:,end) = reshape(temp(3,:),Str_REF.imSz1,Str_REF.imSz2);
temp1 = [Str_REF.locX(1,1,1) Str_REF.locY(1,1,1) Str_REF.locZ(1,1,1)];
temp2 = [Str_REF.locX(1,1,end) Str_REF.locY(1,1,end) Str_REF.locZ(1,1,end)];
Str_REF.voxDim3 = round(norm(temp1-temp2)/(Str_REF.imSz3-1)*1e5)/1e5;

Str_REF.voxDim1=infoCT.PixelSpacing(1);
Str_REF.voxDim2=infoCT.PixelSpacing(2);

vect3 = cross(Str_REF.IOP(1:3),Str_REF.IOP(4:6));
temp = vect3*Str_REF.voxDim3;
temp1 = temp(1);
temp2 = temp(2); 
temp3 = temp(3); 

idx = round((Str_REF.IPP-repmat(Str_REF.IPP(:,end),1,Str_REF.imSz3))./repmat([temp1; temp2; temp3],1,Str_REF.imSz3));
realIdx = find(~isnan(idx(:,round(size(idx,2)/2))) & ~isinf(idx(:,round(size(idx,2)/2))) & idx(:,round(size(idx,2)/2))~=0);
idx = idx(realIdx(1),:); 
Str_REF.IPP = repmat(Str_REF.IPP(:,end),1,Str_REF.imSz3)+repmat(idx,3,1).*repmat([temp1; temp2; temp3],1,Str_REF.imSz3);

vect1 = Str_REF.IOP(1:3);
vect2 = Str_REF.IOP(4:6);
vect3 = cross(vect1, vect2);

Str_REF.voxDim1 = single(Str_REF.voxDim1);
Str_REF.voxDim2 = single(Str_REF.voxDim2);

xr = Str_REF.IOP(1);
yr = Str_REF.IOP(2);
zr = Str_REF.IOP(3);
xc = Str_REF.IOP(4);
yc = Str_REF.IOP(5);
zc = Str_REF.IOP(6);
xs = yr*zc-yc*zr;
ys = zr*xc-zc*xr;
zs = xr*yc-xc*yr;
rot = [xr xc xs; yr yc ys; zr zc zs];

[temp2,temp1] = meshgrid(0:Str_REF.imSz2-1,0:Str_REF.imSz1-1);

offsets = rot(:,1) * temp1(:)' * Str_REF.voxDim1 + rot(:,2) * temp2(:)' * Str_REF.voxDim2;
offsetX = reshape(offsets(1,:),Str_REF.imSz1,Str_REF.imSz2);
offsetY = reshape(offsets(2,:),Str_REF.imSz1,Str_REF.imSz2);
offsetZ = reshape(offsets(3,:),Str_REF.imSz1,Str_REF.imSz2);

tempX = zeros([size(offsetX) Str_REF.imSz3]);
tempY = zeros([size(offsetY) Str_REF.imSz3]);
tempZ = zeros([size(offsetZ) Str_REF.imSz3]);
for n=1:Str_REF.imSz3
    tempX(:,:,n) = offsetX;
    tempY(:,:,n) = offsetY;
    tempZ(:,:,n) = offsetZ;
end    
locX = reshape(repmat(Str_REF.IPP(1,:),Str_REF.imSz1*Str_REF.imSz2,1),Str_REF.imSz1,Str_REF.imSz2,Str_REF.imSz3)+tempX;
locY = reshape(repmat(Str_REF.IPP(2,:),Str_REF.imSz1*Str_REF.imSz2,1),Str_REF.imSz1,Str_REF.imSz2,Str_REF.imSz3)+tempY;
locZ = reshape(repmat(Str_REF.IPP(3,:),Str_REF.imSz1*Str_REF.imSz2,1),Str_REF.imSz1,Str_REF.imSz2,Str_REF.imSz3)+tempZ;

cntr1 = round(Str_REF.imSz1/2);
cntr2 = round(Str_REF.imSz2/2);
cntr3 = round(Str_REF.imSz3/2);

bedPts1 = vect1' * [locX(1,cntr2,cntr3) locY(1,cntr2,cntr3) locZ(1,cntr2,cntr3); ...
    locX(end,cntr2,cntr3) locY(end,cntr2,cntr3) locZ(end,cntr2,cntr3)]';
bedPts2 = vect2' * [locX(cntr1,1,cntr3) locY(cntr1,1,cntr3) locZ(cntr1,1,cntr3); ...
    locX(cntr1,end,cntr3) locY(cntr1,end,cntr3) locZ(cntr1,end,cntr3)]';
bedPts3 = vect3' * [locX(cntr1,cntr2,1) locY(cntr1,cntr2,1) locZ(cntr1,cntr2,1); ...
    locX(cntr1,cntr2,end) locY(cntr1,cntr2,end) locZ(cntr1,cntr2,end)]';


if bedPts1(1)<=bedPts1(2)
    Str_REF.bedRange1 = [bedPts1(1)-abs(Str_REF.voxDim1)/2 bedPts1(2)+abs(Str_REF.voxDim1)/2];
else
    Str_REF.bedRange1 = [bedPts1(1)+abs(Str_REF.voxDim1)/2 bedPts1(2)-abs(Str_REF.voxDim1)/2];
end
if bedPts2(1)<=bedPts2(2)
    Str_REF.bedRange2 = [bedPts2(1)-abs(Str_REF.voxDim2)/2 bedPts2(2)+abs(Str_REF.voxDim2)/2];
else
    Str_REF.bedRange2 = [bedPts2(1)+abs(Str_REF.voxDim2)/2 bedPts2(2)-abs(Str_REF.voxDim2)/2];
end
if bedPts3(1)<=bedPts3(2)
    Str_REF.bedRange3 = [bedPts3(1)-abs(Str_REF.voxDim3)/2 bedPts3(2)+abs(Str_REF.voxDim3)/2];
else
    Str_REF.bedRange3 = [bedPts3(1)+abs(Str_REF.voxDim3)/2 bedPts3(2)-abs(Str_REF.voxDim3)/2];
end


Str_REF.locX = locX;
Str_REF.locY = locY;
Str_REF.locZ = locZ;

        
if isfield(Str_REF,'locX') && ~isa(Str_REF.locX,'single')
    Str_REF.locX = single(Str_REF.locX);
    Str_REF.locY = single(Str_REF.locY);
    Str_REF.locZ = single(Str_REF.locZ);
end

%PET%

Str_FLT=struct;
Str_FLT.nSeries=1;
Str_FLT.seriesDate = infoPET.SeriesDate;
Str_FLT.seriesTime = infoPET.SeriesTime;
Str_FLT.modality = infoPET.Modality;
Str_FLT.gantryModel =infoPET.ManufacturerModelName;
Str_FLT.volumes = FLT;
Str_FLT.IOP = infoPET.ImageOrientationPatient;
for i=length(names1):-1:1
    t=dicominfo(fullfile(fileFolder1,names1{i}));
    Str_FLT.IPP(:,i)=t.ImagePositionPatient;
end
Str_FLT.imSz1 = size(Str_FLT.volumes,1);
Str_FLT.imSz2 = size(Str_FLT.volumes,2);
Str_FLT.imSz3 = size(Str_FLT.volumes,3);


[temp2,temp1] = meshgrid(0:Str_FLT.imSz2-1,0:Str_FLT.imSz1-1); 
Str_FLT.locX = zeros(Str_FLT.imSz1,Str_FLT.imSz2,Str_FLT.imSz3);
Str_FLT.locY = zeros(Str_FLT.imSz1,Str_FLT.imSz2,Str_FLT.imSz3);
Str_FLT.locZ = zeros(Str_FLT.imSz1,Str_FLT.imSz2,Str_FLT.imSz3);

temp = repmat(Str_FLT.IPP(:,1),1,Str_FLT.imSz1*Str_FLT.imSz2)+[Str_FLT.IOP(1) Str_FLT.IOP(2) Str_FLT.IOP(3)]'*temp1(:)'*infoPET.PixelSpacing(2)+[Str_FLT.IOP(4) Str_FLT.IOP(5) Str_FLT.IOP(6)]'*temp2(:)'*infoPET.PixelSpacing(1);
Str_FLT.locX(:,:,1) = reshape(temp(1,:),Str_FLT.imSz1,Str_FLT.imSz2);
Str_FLT.locY(:,:,1) = reshape(temp(2,:),Str_FLT.imSz1,Str_FLT.imSz2);
Str_FLT.locZ(:,:,1) = reshape(temp(3,:),Str_FLT.imSz1,Str_FLT.imSz2);

temp = repmat(Str_FLT.IPP(:,end),1,Str_FLT.imSz1*Str_FLT.imSz2)+[Str_FLT.IOP(1) Str_FLT.IOP(2) Str_FLT.IOP(3)]'*temp1(:)'*infoPET.PixelSpacing(2)+[Str_FLT.IOP(4) Str_FLT.IOP(5) Str_FLT.IOP(6)]'*temp2(:)'*infoPET.PixelSpacing(1);
Str_FLT.locX(:,:,end) = reshape(temp(1,:),Str_FLT.imSz1,Str_FLT.imSz2);
Str_FLT.locY(:,:,end) = reshape(temp(2,:),Str_FLT.imSz1,Str_FLT.imSz2);
Str_FLT.locZ(:,:,end) = reshape(temp(3,:),Str_FLT.imSz1,Str_FLT.imSz2);
temp1 = [Str_FLT.locX(1,1,1) Str_FLT.locY(1,1,1) Str_FLT.locZ(1,1,1)];
temp2 = [Str_FLT.locX(1,1,end) Str_FLT.locY(1,1,end) Str_FLT.locZ(1,1,end)];
Str_FLT.voxDim3 = round(norm(temp1-temp2)/(Str_FLT.imSz3-1)*1e5)/1e5;

Str_FLT.voxDim1=infoPET.PixelSpacing(1);
Str_FLT.voxDim2=infoPET.PixelSpacing(2);

vect3 = cross(Str_FLT.IOP(1:3),Str_FLT.IOP(4:6));
temp = vect3*Str_FLT.voxDim3;
temp1 = temp(1);
temp2 = temp(2); 
temp3 = temp(3); 


idx = round((Str_FLT.IPP-repmat(Str_FLT.IPP(:,end),1,Str_FLT.imSz3))./repmat([temp1; temp2; temp3],1,Str_FLT.imSz3));
realIdx = find(~isnan(idx(:,round(size(idx,2)/2))) & ~isinf(idx(:,round(size(idx,2)/2))) & idx(:,round(size(idx,2)/2))~=0);
idx = idx(realIdx(1),:); 
Str_FLT.IPP = repmat(Str_FLT.IPP(:,end),1,Str_FLT.imSz3)+repmat(idx,3,1).*repmat([temp1; temp2; temp3],1,Str_FLT.imSz3);

vect1 = Str_FLT.IOP(1:3);
vect2 = Str_FLT.IOP(4:6);
vect3 = cross(vect1, vect2);


Str_FLT.voxDim1 = single(Str_FLT.voxDim1);
Str_FLT.voxDim2 = single(Str_FLT.voxDim2);

xr = Str_FLT.IOP(1);
yr = Str_FLT.IOP(2);
zr = Str_FLT.IOP(3);
xc = Str_FLT.IOP(4);
yc = Str_FLT.IOP(5);
zc = Str_FLT.IOP(6);
xs = yr*zc-yc*zr;
ys = zr*xc-zc*xr;
zs = xr*yc-xc*yr;
rot = [xr xc xs; yr yc ys; zr zc zs];

[temp2,temp1] = meshgrid(0:Str_FLT.imSz2-1,0:Str_FLT.imSz1-1);

offsets = rot(:,1) * temp1(:)' * Str_FLT.voxDim1 + rot(:,2) * temp2(:)' * Str_FLT.voxDim2;
offsetX = reshape(offsets(1,:),Str_FLT.imSz1,Str_FLT.imSz2);
offsetY = reshape(offsets(2,:),Str_FLT.imSz1,Str_FLT.imSz2);
offsetZ = reshape(offsets(3,:),Str_FLT.imSz1,Str_FLT.imSz2);

tempX = zeros([size(offsetX) Str_FLT.imSz3]);
tempY = zeros([size(offsetY) Str_FLT.imSz3]);
tempZ = zeros([size(offsetZ) Str_FLT.imSz3]);
for n=1:Str_FLT.imSz3
    tempX(:,:,n) = offsetX;
    tempY(:,:,n) = offsetY;
    tempZ(:,:,n) = offsetZ;
end    
locX = reshape(repmat(Str_FLT.IPP(1,:),Str_FLT.imSz1*Str_FLT.imSz2,1),Str_FLT.imSz1,Str_FLT.imSz2,Str_FLT.imSz3)+tempX;
locY = reshape(repmat(Str_FLT.IPP(2,:),Str_FLT.imSz1*Str_FLT.imSz2,1),Str_FLT.imSz1,Str_FLT.imSz2,Str_FLT.imSz3)+tempY;
locZ = reshape(repmat(Str_FLT.IPP(3,:),Str_FLT.imSz1*Str_FLT.imSz2,1),Str_FLT.imSz1,Str_FLT.imSz2,Str_FLT.imSz3)+tempZ;


cntr1 = round(Str_FLT.imSz1/2);
cntr2 = round(Str_FLT.imSz2/2);
cntr3 = round(Str_FLT.imSz3/2);

bedPts1 = vect1' * [locX(1,cntr2,cntr3) locY(1,cntr2,cntr3) locZ(1,cntr2,cntr3); ...
    locX(end,cntr2,cntr3) locY(end,cntr2,cntr3) locZ(end,cntr2,cntr3)]';
bedPts2 = vect2' * [locX(cntr1,1,cntr3) locY(cntr1,1,cntr3) locZ(cntr1,1,cntr3); ...
    locX(cntr1,end,cntr3) locY(cntr1,end,cntr3) locZ(cntr1,end,cntr3)]';
bedPts3 = vect3' * [locX(cntr1,cntr2,1) locY(cntr1,cntr2,1) locZ(cntr1,cntr2,1); ...
    locX(cntr1,cntr2,end) locY(cntr1,cntr2,end) locZ(cntr1,cntr2,end)]';


if bedPts1(1)<=bedPts1(2)
    Str_FLT.bedRange1 = [bedPts1(1)-abs(Str_FLT.voxDim1)/2 bedPts1(2)+abs(Str_FLT.voxDim1)/2];
else
    Str_FLT.bedRange1 = [bedPts1(1)+abs(Str_FLT.voxDim1)/2 bedPts1(2)-abs(Str_FLT.voxDim1)/2];
end
if bedPts2(1)<=bedPts2(2)
    Str_FLT.bedRange2 = [bedPts2(1)-abs(Str_FLT.voxDim2)/2 bedPts2(2)+abs(Str_FLT.voxDim2)/2];
else
    Str_FLT.bedRange2 = [bedPts2(1)+abs(Str_FLT.voxDim2)/2 bedPts2(2)-abs(Str_FLT.voxDim2)/2];
end
if bedPts3(1)<=bedPts3(2)
    Str_FLT.bedRange3 = [bedPts3(1)-abs(Str_FLT.voxDim3)/2 bedPts3(2)+abs(Str_FLT.voxDim3)/2];
else
    Str_FLT.bedRange3 = [bedPts3(1)+abs(Str_FLT.voxDim3)/2 bedPts3(2)-abs(Str_FLT.voxDim3)/2];
end


Str_FLT.locX = locX;
Str_FLT.locY = locY;
Str_FLT.locZ = locZ;

        
if isfield(Str_FLT,'locX') && ~isa(Str_FLT.locX,'single')
    Str_FLT.locX = single(Str_FLT.locX);
    Str_FLT.locY = single(Str_FLT.locY);
    Str_FLT.locZ = single(Str_FLT.locZ);
end

%Final%

Final = Str_FLT;
Final.locX = Str_REF.locX;
Final.locY = Str_REF.locY;
Final.locZ = Str_REF.locZ;
Final.bedRange1 = Str_REF.bedRange1;
Final.bedRange2 = Str_REF.bedRange2;
Final.bedRange3 = Str_REF.bedRange3;
Final.IOP = Str_REF.IOP;
Final.IPP = Str_REF.IPP;

rot_1 = [Str_FLT.IOP(1:3) Str_FLT.IOP(4:6) cross(Str_FLT.IOP(1:3),Str_FLT.IOP(4:6))];
rot_2 = [Str_REF.IOP(1:3) Str_REF.IOP(4:6) cross(Str_REF.IOP(1:3),Str_REF.IOP(4:6))];

vol = Str_FLT.volumes;
bak = vol(1);

clear temp
newIOP(1:3) = Str_REF.IOP(1:3)/norm(Str_REF.IOP(1:3));
newIOP(4:6) = Str_REF.IOP(4:6)/norm(Str_REF.IOP(4:6));
xr = newIOP(1);
yr = newIOP(2);
zr = newIOP(3);
xc = newIOP(4);
yc = newIOP(5);
zc = newIOP(6);
xs = yr*zc-yc*zr;
ys = zr*xc-zc*xr;
zs = xr*yc-xc*yr;
newRot = [xr xc xs; yr yc ys; zr zc zs];
oldLocX = Str_FLT.locX;
oldLocY = Str_FLT.locY;
oldLocZ = Str_FLT.locZ;
oldImSz1 = size(oldLocX,1);
oldImSz2 = size(oldLocX,2);
oldImSz3 = size(oldLocX,3);
oldIOP = Str_FLT.IOP;
temp.oldVoxDim1 = round(diff(double(Str_FLT.bedRange1))/oldImSz1*1e5)/1e5;
temp.oldVoxDim2 = round(diff(double(Str_FLT.bedRange2))/oldImSz2*1e5)/1e5;
temp.oldVoxDim3 = round(diff(double(Str_FLT.bedRange3))/oldImSz3*1e5)/1e5;
xr = oldIOP(1);
yr = oldIOP(2);
zr = oldIOP(3);
xc = oldIOP(4);
yc = oldIOP(5);
zc = oldIOP(6);
xs = yr*zc-yc*zr;
ys = zr*xc-zc*xr;
zs = xr*yc-xc*yr;
oldRot = [xr xc xs; yr yc ys; zr zc zs];
oldFOV1 = temp.oldVoxDim1 * oldImSz1;
oldFOV2 = temp.oldVoxDim2 * oldImSz2;
oldFOV3 = temp.oldVoxDim3 * oldImSz3;


newIOP(1:3) = newIOP(1:3)/norm(newIOP(1:3)); 
newIOP(4:6) = newIOP(4:6)/norm(newIOP(4:6));
xr = oldIOP(1);
yr = oldIOP(2);
zr = oldIOP(3);
xc = oldIOP(4);
yc = oldIOP(5);
zc = oldIOP(6);
xs = yr*zc-yc*zr;
ys = zr*xc-zc*xr;
zs = xr*yc-xc*yr;
oldRot = [xr xc xs; yr yc ys; zr zc zs];
xr = newIOP(1);
yr = newIOP(2);
zr = newIOP(3);
xc = newIOP(4);
yc = newIOP(5);
zc = newIOP(6);
xs = yr*zc-yc*zr;
ys = zr*xc-zc*xr;
zs = xr*yc-xc*yr;
newRot = [xr xc xs; yr yc ys; zr zc zs];
rot = oldRot'*newRot;
tmp = sum(abs(rot'*[oldFOV1 0 0; 0 oldFOV2 0; 0 0 oldFOV3]),2);
newFOV1 = tmp(1);
newFOV2 = tmp(2);
newFOV3 = tmp(3);

newIOP(1:3) = newIOP(1:3)/norm(newIOP(1:3)); 
newIOP(4:6) = newIOP(4:6)/norm(newIOP(4:6));
xr = oldIOP(1);
yr = oldIOP(2);
zr = oldIOP(3);
xc = oldIOP(4);
yc = oldIOP(5);
zc = oldIOP(6);
xs = yr*zc-yc*zr;
ys = zr*xc-zc*xr;
zs = xr*yc-xc*yr;
oldRot = [xr xc xs; yr yc ys; zr zc zs];
xr = newIOP(1);
yr = newIOP(2);
zr = newIOP(3);
xc = newIOP(4);
yc = newIOP(5);
zc = newIOP(6);
xs = yr*zc-yc*zr;
ys = zr*xc-zc*xr;
zs = xr*yc-xc*yr;
newRot = [xr xc xs; yr yc ys; zr zc zs];
rot = oldRot'*newRot;
tmp = sum(abs(rot'*[oldImSz1 0 0; 0 oldImSz2 0; 0 0 oldImSz3]),2);
newImSz1 = tmp(1);
newImSz2 = tmp(2);
newImSz3 = tmp(3);

newImSz1 = round(newImSz1);
newImSz2 = round(newImSz2);
newImSz3 = round(newImSz3);
temp.newVoxDim1 = round(newFOV1/newImSz1*1e5)/1e5;
temp.newVoxDim2 = round(newFOV2/newImSz2*1e5)/1e5;
temp.newVoxDim3 = round(newFOV3/newImSz3*1e5)/1e5;

oldRotx = [oldIOP(1:3) oldIOP(4:6) cross(oldIOP(1:3),oldIOP(4:6))];
newRot=oldRot';
prec = 1e9; 
totRot = round(newRot * oldRotx * prec) / prec; 
oldRotx = round(oldRotx * prec) / prec;
newRot = round(newRot * prec) / prec;

temp.oldInterpX = oldLocX;
temp.oldInterpY = oldLocY;
temp.oldInterpZ = oldLocZ;

[temp.oldInterpY,temp.oldInterpX,temp.oldInterpZ] = meshgrid(squeeze(temp.oldInterpY(1,1:end,1)),squeeze(temp.oldInterpX(1:end,1,1)),squeeze(temp.oldInterpZ(1,1,1:end)));
temp.newVoxDim3 = -temp.newVoxDim3;
prec = 1e9;
vectTest = round((oldRot'*newRot)*prec)/prec;


oldRotx = [Str_REF.IOP(1:3) Str_REF.IOP(4:6) cross(Str_REF.IOP(1:3),Str_REF.IOP(4:6))];
newRot=rot_1';
prec = 1e9; 
totRot = round(newRot * oldRotx * prec) / prec; 
oldRotx = round(oldRotx * prec) / prec;
newRot = round(newRot * prec) / prec;

interpOutX = Str_REF.locX;
interpOutY = Str_REF.locY;
interpOutZ = Str_REF.locZ;

              
cst = 0;
if ~(isa(vol,'single') || isa(vol,'double'))
        origClass = class(vol);
        vol = single(vol);
        cst = 1;
end

temp.oldInterpZ = flipdim(temp.oldInterpZ,3);
vol = flipdim(vol,3);
outVol = zeros(size(interpOutX,1),size(interpOutX,2),size(interpOutX,3),size(vol,4),'like',vol);
F = griddedInterpolant(temp.oldInterpX,temp.oldInterpY,temp.oldInterpZ,vol,'linear','none');
outVol = F(interpOutX,interpOutY,interpOutZ);

outVol(isnan(outVol)) = bak;

Final.volumes = outVol;
Final.imSz1 = size(outVol,1);
Final.imSz2 = size(outVol,2);
Final.imSz3 = size(outVol,3);

mkdir PET_Preprocessed

%disp(PET_Preprocessed)

for i=1:1:size(Final.volumes,3)
    pet_pp=uint16(Final.volumes(:,:,i));
    s0= PET_Preprocessed;
    s01 = '/PET_Preprocessed/';
    s='IM';
    s1='.dcm';
    s2=num2str(i-1);
    dicomwrite(pet_pp,strcat(s0,s01,s,s2,s1));
end

exit()