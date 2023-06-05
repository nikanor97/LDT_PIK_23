import React, {useEffect, useRef, useState} from "react";
import {STLLoader} from "three/examples/jsm/loaders/STLLoader";
import {OrbitControls} from "three/examples/jsm/controls/OrbitControls";
import * as THREE from "three";

interface Props {
  fileUrl: File;
}

const STLViewer: React.FC<Props> = ({fileUrl}) => {
    const containerRef = useRef<HTMLDivElement>(null);
    const [url, setUrl] = useState<string>();

    useEffect(() => {
        const reader = new FileReader();
        reader.onload = (event) => {
            setUrl(URL.createObjectURL(new Blob([new Uint8Array(event.target?.result as any)], {type: fileUrl.type})));
        };
        reader.readAsArrayBuffer(fileUrl);
    }, [fileUrl]);

    useEffect(() => {
        if (!containerRef.current) return;
        if (!url) return;
        console.log(url);

        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(26, 400 / 400, 1, 100000);
        const renderer = new THREE.WebGLRenderer();
        renderer.setSize(600, 600);
        renderer.setClearColor(0xF9FAFB);
        containerRef.current.appendChild(renderer.domElement);

        const controls = new OrbitControls(camera, renderer.domElement);
        controls.rotateSpeed = 1.0;
        controls.zoomSpeed = 1.2;
        controls.panSpeed = 0.8;

        const directionalLight = new THREE.DirectionalLight(0xffffee, 1.5);
        scene.add(directionalLight);
        scene.add(new THREE.AmbientLight(0xffffee, 0.4));

        const loader = new STLLoader();
        loader.load(
            url,
            (geometry) => {
                const material = new THREE.MeshStandardMaterial({color: 0xFC4C02});
                const mesh = new THREE.Mesh(geometry, material);
        
                // Определение границ и центра объекта для корректного позиционирования
                const box = new THREE.Box3().setFromObject(mesh);
                const size = box.getSize(new THREE.Vector3()).length();
                const center = box.getCenter(new THREE.Vector3());

                controls.reset();

                camera.position.copy(center);
                camera.position.x += size / 2.0;
                camera.position.y += size / 2.0;
                camera.position.z += size / 2.0;
                camera.lookAt(center);

                controls.maxDistance = size * 10;
                controls.target.copy(center);

                scene.add(mesh);
            },
            undefined,
            (error) => {
                console.error("An error happened", error);
            }
        );

        const animate = () => {
            requestAnimationFrame(animate);
            controls.update();
            renderer.render(scene, camera);
        };

        animate();

        return () => {
            renderer.dispose();
            scene.clear();
            containerRef.current?.removeChild(renderer.domElement);
        };
    }, [url]);

    return <div ref={containerRef} />;
};

export default STLViewer;
