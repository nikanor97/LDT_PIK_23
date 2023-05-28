const transformData = (inputObj) => {
    const {project, ...rest} = inputObj;

    const transformedObj = {
        project,
        values: []
    };
  
    Object.keys(rest).forEach((key) => {
        const deviceType = key.replace(/[XYZ]$/, "");
        const axis = key.charAt(key.length - 1).toUpperCase();
  
        const existingDevice = transformedObj.values.find((item) => item.deviceType === deviceType);
        if (existingDevice) {
            existingDevice[axis] = inputObj[key];
        } else {
            const newDevice = {
                deviceType,
                [axis]: inputObj[key]
            };
            transformedObj.values.push(newDevice);
        }
    });
  
    return transformedObj;
};
  
export default transformData;
