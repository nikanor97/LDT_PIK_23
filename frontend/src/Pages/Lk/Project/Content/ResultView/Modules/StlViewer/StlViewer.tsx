import React, {useEffect, useRef, useState} from "react";
import {STLLoader} from "three/examples/jsm/loaders/STLLoader";
import {OrbitControls} from "three/examples/jsm/controls/OrbitControls";
import * as THREE from "three";
import styles from "./StlViewer.module.less";

interface Props {
  file: File;
}

const STLViewer: React.FC<Props> = ({file}) => {
    const containerRef = useRef<HTMLDivElement>(null);
    const [url, setUrl] = useState<string>();

    useEffect(() => {
        const reader = new FileReader();
        reader.onload = (event) => {
            setUrl(URL.createObjectURL(new Blob([new Uint8Array(event.target?.result as ArrayBufferLike)], {type: file.type})));
        };
        reader.readAsArrayBuffer(file);
    }, [file]);

    useEffect(() => {
        if (!containerRef.current) return;
        if (!url) return;

        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(26, containerRef.current.offsetWidth / containerRef.current.offsetHeight, 1, 100000);
        const renderer = new THREE.WebGLRenderer();
        renderer.setSize(containerRef.current.offsetWidth, containerRef.current.offsetHeight);
        renderer.setClearColor(0xE3E3E3);
        containerRef.current.appendChild(renderer.domElement);

        const controls = new OrbitControls(camera, renderer.domElement);
        controls.rotateSpeed = 1.0;
        controls.zoomSpeed = 1.2;
        controls.panSpeed = 0.8;

        //Directional Light
        const directionalLight = new THREE.DirectionalLight(0xffffff, 1.8);
        scene.add(directionalLight);

        //AmbientLight
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.7);
        scene.add(ambientLight);

        //Point Light
        const pointLight = new THREE.PointLight( 0xffffff, 0.8 );
        scene.add( pointLight );

        const loader = new STLLoader();
        loader.load(
            url,
            (geometry) => {
                const material = new THREE.MeshPhongMaterial({color: 0x8C8C8C});
                const mesh = new THREE.Mesh(geometry, material);
        
                // Определение границ и центра объекта для корректного позиционирования
                const box = new THREE.Box3().setFromObject(mesh);
                const size = box.getSize(new THREE.Vector3()).length();
                const center = box.getCenter(new THREE.Vector3());

                controls.reset();

                camera.position.copy(center);
                camera.position.x += size / 0.8;
                camera.position.y += size / 0.8;
                camera.position.z += size / 0.8;
                camera.lookAt(center);

                controls.maxDistance = size * 10;
                controls.target.copy(center);

                scene.add(mesh);
            },
            undefined,
            (error) => {
                console.error("При создании 3D элемента произошла ошибка", error);
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

    return <div ref={containerRef} className={styles.stl}/>;
};

export default STLViewer;
