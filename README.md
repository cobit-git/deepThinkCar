<!-- Output copied to clipboard! -->

<!-----
NEW: Check the "Suppress top comment" option to remove this info from the output.

Conversion time: 0.444 seconds.


Using this Markdown file:

1. Paste this output into your source file.
2. See the notes and action items below regarding this conversion run.
3. Check the rendered output (headings, lists, code blocks, tables) for proper
   formatting and use a linkchecker before you publish this page.

Conversion notes:

* Docs to Markdown version 1.0β30
* Tue Jul 13 2021 05:58:47 GMT-0700 (PDT)
* Source doc: Untitled document
* This document has images: check for >>>>>  gd2md-html alert:  inline image link in generated source and store images to your server. NOTE: Images in exported zip file from Google Docs may not appear in  the same order as they do in your doc. Please check the images!

----->


<p style="color: red; font-weight: bold">>>>>>  gd2md-html alert:  ERRORs: 0; WARNINGs: 0; ALERTS: 1.</p>
<ul style="color: red; font-weight: bold"><li>See top comment block for details on ERRORs and WARNINGs. <li>In the converted Markdown or HTML, search for inline alerts that start with >>>>>  gd2md-html alert:  for specific instances that need correction.</ul>

<p style="color: red; font-weight: bold">Links to alert messages:</p><a href="#gdcalert1">alert1</a>

<p style="color: red; font-weight: bold">>>>>> PLEASE check and correct alert issues and delete this message and the inline alerts.<hr></p>


**이것은 테스트로 만드는 문서다 씨발 **

lang:python

   try:

        i = 0

        while cap.isOpened():

            _, img_org = cap.read()

            

            lanes, img_lane = cv_detector.get_lane(img_org)

            angle_lane, img_lane = cv_detector.get_steering_angle(img_lane, lanes)

            

            prev_time = time.time()

            angle_deep, img_deep = deep_detector.follow_lane(img_org)

            curr_time = time.time()

            diff = angle_lane - angle_deep

            print(angle_deep, angle_lane, curr_time-prev_time)

            cv2.imshow("Deep Learning", img_deep)

            if cv2.waitKey(1) & 0xFF == ord('q'):

                break

    finally:

        cap.release()

        cv2.destroyAllWindows()

이거 제대로 동작 하는 것이냐?



<p id="gdcalert1" ><span style="color: red; font-weight: bold">>>>>>  gd2md-html alert: inline image link here (to images/image1.jpg). Store image on your image server and adjust path/filename/extension if necessary. </span><br>(<a href="#">Back to top</a>)(<a href="#gdcalert2">Next alert</a>)<br><span style="color: red; font-weight: bold">>>>>> </span></p>


![alt_text](images/image1.jpg "image_tooltip")
