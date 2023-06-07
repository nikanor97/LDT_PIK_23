const transformData = (inputObj) => {
    const {project_id, dxf_file_id, ...rest} = inputObj;

    const transformedObj = {
        project_id,
        dxf_file_id,
        devices: []
    };
  
    Object.keys(rest).forEach((key) => {
        const splitedKey = key.split("/");
        // const type = key.replace(/[XYZ]$/, "");
        const type = splitedKey[0];
        const id = splitedKey[1];
        const name = splitedKey[2];

        const axis = key.charAt(key.length - 1).toUpperCase();
  
        const existingDevice = transformedObj.devices.find((item) => item.type === type);
        if (existingDevice) {
            existingDevice[`coord_${axis.toLocaleLowerCase()}`] = inputObj[key];
        } else {
            const newDevice = {
                type,
                id,
                name,
                [`coord_${axis.toLocaleLowerCase()}`]: inputObj[key]
            };
            transformedObj.devices.push(newDevice);
        }
    });
  
    return transformedObj;
};
  
export default transformData;
