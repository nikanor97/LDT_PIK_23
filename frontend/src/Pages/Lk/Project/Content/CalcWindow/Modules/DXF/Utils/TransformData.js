const transformData = (inputObj) => {
    const {project_id, dxf_file_id, ...rest} = inputObj;

    const transformedObj = {
        project_id,
        dxf_file_id,
        devices: []
    };
  
    Object.keys(rest).forEach((key) => {
        const type = key.replace(/[XYZ]$/, "");
        const axis = key.charAt(key.length - 1).toUpperCase();
  
        const existingDevice = transformedObj.devices.find((item) => item.type === type);
        if (existingDevice) {
            existingDevice[`coord_${axis.toLocaleLowerCase()}`] = inputObj[key];
        } else {
            const newDevice = {
                type,
                [`coord_${axis.toLocaleLowerCase()}`]: inputObj[key]
            };
            transformedObj.devices.push(newDevice);
        }
    });
  
    return transformedObj;
};
  
export default transformData;
